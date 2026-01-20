import requests
import json
import os
import datetime
import socket
import sqlite3

# --- CONFIGURAÇÕES FIREBASE ---
PROJECT_ID = "marmoraria-app"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# --- CONFIGURAÇÕES SQLITE (LOCAL) ---
DB_NAME = "marmoraria_local.db"

def init_local_db():
    """Cria as tabelas locais caso não existam"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabelas principais espelhando as coleções do Firebase
    # A coluna 'dados_json' guarda o conteúdo completo do documento
    # A coluna 'pendente' indica se precisa ser enviado ao Firebase (0=Não, 1=Sim)
    tabelas = ["estoque", "financeiro", "orcamentos", "users", "movimentacoes"]
    for tabela in tabelas:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {tabela} (
                id TEXT PRIMARY KEY,
                dados_json TEXT,
                pendente INTEGER DEFAULT 0
            )
        ''')
    conn.commit()
    conn.close()

# Inicializa o banco assim que o serviço é importado
init_local_db()

# =========================================================
# =================== LÓGICA DE CONEXÃO ===================
# =========================================================

def verificar_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# =========================================================
# ================= CONVERSORES FIRESTORE =================
# =========================================================

def _converter_para_firestore(dados):
    fields = {}
    for k, v in dados.items():
        if v is None: fields[k] = {"nullValue": None}
        elif isinstance(v, bool): fields[k] = {"booleanValue": v}
        elif isinstance(v, int): fields[k] = {"integerValue": str(v)}
        elif isinstance(v, float): fields[k] = {"doubleValue": v}
        elif isinstance(v, list):
            vals = []
            for item in v:
                if isinstance(item, dict): vals.append({"mapValue": _converter_para_firestore(item)})
                else: vals.append({"stringValue": str(item)})
            fields[k] = {"arrayValue": {"values": vals}}
        elif isinstance(v, dict): fields[k] = {"mapValue": _converter_para_firestore(v)}
        else: fields[k] = {"stringValue": str(v)}
    return {"fields": fields}

def _extrair_valor(v):
    if 'stringValue' in v: return v['stringValue']
    if 'integerValue' in v: return int(v['integerValue'])
    if 'doubleValue' in v: return float(v['doubleValue'])
    if 'booleanValue' in v: return v['booleanValue']
    if 'nullValue' in v: return None
    if 'mapValue' in v:
        res = {}
        for k2, v2 in v['mapValue'].get('fields', {}).items():
            res[k2] = _extrair_valor(v2)
        return res
    if 'arrayValue' in v:
        return [_extrair_valor(item) for item in v['arrayValue'].get('values', [])]
    return str(v)

# =========================================================
# ================= NÚCLEO DE DADOS (CACHE) ===============
# =========================================================

def save_local(collection, doc_id, dados, pendente=0):
    """Salva ou atualiza um documento no SQLite local"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    dados_str = json.dumps(dados)
    cursor.execute(f"INSERT OR REPLACE INTO {collection} (id, dados_json, pendente) VALUES (?, ?, ?)",
                   (doc_id, dados_str, pendente))
    conn.commit()
    conn.close()

def get_local(collection):
    """Busca todos os itens de uma coleção no SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT dados_json FROM {collection}")
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

# =========================================================
# ================= CRUD PRINCIPAL (HÍBRIDO) ==============
# =========================================================

def get_collection(collection):
    """Tenta buscar do Firebase e atualiza o Cache. Se falhar, usa o Cache."""
    if verificar_conexao():
        try:
            res = requests.get(f"{BASE_URL}/{collection}", timeout=5)
            if res.status_code == 200:
                documentos = []
                data = res.json()
                if 'documents' in data:
                    for doc in data['documents']:
                        obj = {}
                        obj['id'] = doc['name'].split('/')[-1]
                        for k, v in doc.get('fields', {}).items():
                            obj[k] = _extrair_valor(v)
                        documentos.append(obj)
                        # Atualiza o cache local para cada documento vindo da nuvem
                        save_local(collection, obj['id'], obj, pendente=0)
                return documentos
        except:
            pass
    # Se estiver offline ou o request der erro, retorna o que tem no celular
    return get_local(collection)

def add_document(collection, dados):
    """Salva no Firebase se houver net. Se não, salva localmente como pendente."""
    doc_id = dados.get("id") or f"local_{int(datetime.datetime.now().timestamp())}"
    dados["id"] = doc_id
    
    sucesso_nuvem = False
    if verificar_conexao():
        try:
            payload = _converter_para_firestore(dados)
            res = requests.patch(f"{BASE_URL}/{collection}/{doc_id}", json=payload, timeout=5)
            if res.status_code == 200:
                sucesso_nuvem = True
        except:
            pass

    # Salva sempre no local. Se enviou pra nuvem, pendente=0. Se não, pendente=1.
    save_local(collection, doc_id, dados, pendente=0 if sucesso_nuvem else 1)
    return True

def update_document(collection, doc_id, dados):
    return add_document(collection, dados) # Patch no Firebase trata ambos

def delete_document(collection, doc_id):
    if verificar_conexao():
        try:
            requests.delete(f"{BASE_URL}/{collection}/{doc_id}", timeout=5)
        except:
            pass
    # Remove do local também
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {collection} WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    return True

# =========================================================
# ================= FUNÇÕES ESPECÍFICAS ===================
# =========================================================

def get_orcamentos_lista():
    # Ordena por data (o SQLite traz na ordem de inserção por padrão)
    lista = get_collection("orcamentos")
    return sorted(lista, key=lambda x: x.get('data', ''), reverse=True)

def sync_offline_data():
    """Varre o banco local e envia o que foi feito offline para o Firebase"""
    if not verificar_conexao(): return
    
    tabelas = ["estoque", "financeiro", "orcamentos", "movimentacoes"]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for tab in tabelas:
        cursor.execute(f"SELECT id, dados_json FROM {tab} WHERE pendente = 1")
        pendentes = cursor.fetchall()
        for p_id, p_json in pendentes:
            dados = json.loads(p_json)
            # Tenta enviar
            try:
                payload = _converter_para_firestore(dados)
                res = requests.patch(f"{BASE_URL}/{tab}/{p_id}", json=payload, timeout=5)
                if res.status_code == 200:
                    cursor.execute(f"UPDATE {tab} SET pendente = 0 WHERE id = ?", (p_id,))
            except:
                continue
    conn.commit()
    conn.close()

# Re-implementando as funções que o Dashboard e Financeiro usam
def get_collection_count(collection):
    return len(get_collection(collection))

def get_user_doc_by_email(email):
    users = get_collection("users")
    for u in users:
        if u.get("email") == email: return u
    return None

def verify_user_password(email, password):
    user = get_user_doc_by_email(email)
    if user:
        senha_db = str(user.get("senha") or user.get("password") or "")
        return senha_db == str(password)
    return False

# Mantendo compatibilidade com as funções financeiras
def add_movimentacao(tipo, valor, descricao, categoria):
    nova = {
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "categoria": categoria,
        "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    return add_document("movimentacoes", nova)