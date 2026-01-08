import requests
import json
import os
import datetime
import socket

# --- CONFIGURAÇÕES ---
PROJECT_ID = "marmoraria-app"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# --- CONVERSORES AVANÇADOS (CORRIGE O ERRO DE STRING/DICIONÁRIO) ---
def _converter_para_firestore(dados):
    fields = {}
    for k, v in dados.items():
        if v is None: fields[k] = {"nullValue": None}
        elif isinstance(v, bool): fields[k] = {"booleanValue": v}
        elif isinstance(v, int): fields[k] = {"integerValue": str(v)}
        elif isinstance(v, float): fields[k] = {"doubleValue": v}
        elif isinstance(v, list):
            # Se for uma lista de dicionários (como itens do orçamento)
            vals = []
            for item in v:
                if isinstance(item, dict):
                    vals.append({"mapValue": _converter_para_firestore(item)})
                else:
                    vals.append({"stringValue": str(item)})
            fields[k] = {"arrayValue": {"values": vals}}
        elif isinstance(v, dict):
            fields[k] = {"mapValue": _converter_para_firestore(v)}
        else: fields[k] = {"stringValue": str(v)}
    return {"fields": fields}

def _converter_de_firestore(doc):
    name = doc.get('name', '')
    obj = {'id': name.split('/')[-1] if name else 'unknown'}
    if 'fields' in doc:
        for k, v in doc['fields'].items():
            obj[k] = _extrair_valor(v)
    return obj

def _extrair_valor(v):
    """Extrai valor de forma recursiva para lidar com listas e mapas"""
    if 'stringValue' in v: return v['stringValue']
    if 'integerValue' in v: return int(v['integerValue'])
    if 'doubleValue' in v: return float(v['doubleValue'])
    if 'booleanValue' in v: return v['booleanValue']
    if 'nullValue' in v: return None
    if 'arrayValue' in v:
        return [_extrair_valor(x) for x in v['arrayValue'].get('values', [])]
    if 'mapValue' in v:
        res = {}
        for k_sub, v_sub in v['mapValue'].get('fields', {}).items():
            res[k_sub] = _extrair_valor(v_sub)
        return res
    return list(v.values())[0] if v else None

# --- CONEXÃO ---
def initialize_firebase():
    return True

def verificar_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# --- FUNÇÕES GENÉRICAS (ACABA COM ERROS DE ATRIBUTO) ---
def get_collection(collection_name):
    """Busca qualquer coleção"""
    if not verificar_conexao(): return []
    try:
        res = requests.get(f"{BASE_URL}/{collection_name}?pageSize=100")
        if res.status_code == 200 and 'documents' in res.json():
            return [_converter_de_firestore(doc) for doc in res.json()['documents']]
        return []
    except: return []

def add_document(collection, dados):
    if not verificar_conexao(): return False
    try:
        res = requests.post(f"{BASE_URL}/{collection}", json=_converter_para_firestore(dados))
        return res.status_code == 200
    except: return False

def update_document(collection, doc_id, dados):
    """Atualiza um documento via API REST (Padrão do seu arquivo)"""
    if not verificar_conexao(): return False
    try:
        # A API do Firestore exige um PATCH para atualizar
        # Criamos o corpo convertido para o formato do Firebase
        corpo_json = _converter_para_firestore(dados)
        
        # A máscara diz ao Firebase quais campos devem ser alterados
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        
        url = f"{BASE_URL}/{collection}/{doc_id}?{mask}"
        res = requests.patch(url, json=corpo_json)
        
        if res.status_code == 200:
            print(f"Sucesso ao atualizar {doc_id}")
            return True
        else:
            print(f"Erro API Firebase ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"Erro ao atualizar: {e}")
        return False

def delete_document(collection, doc_id):
    if not verificar_conexao(): return False
    try:
        res = requests.delete(f"{BASE_URL}/{collection}/{doc_id}")
        return res.status_code == 200
    except: return False

# --- DASHBOARD / UTILITÁRIOS ---
def get_collection_count(collection):
    return len(get_collection(collection))

def get_faturamento_mes_atual():
    extrato = get_collection("movimentacoes")
    agora = datetime.datetime.now()
    total = 0.0
    for mov in extrato:
        if mov.get('tipo') == 'Entrada':
            try:
                # Tenta converter data iso ou string simples
                data_str = mov.get('data', '')
                data_mov = datetime.datetime.fromisoformat(data_str.replace('Z', ''))
                if data_mov.month == agora.month and data_mov.year == agora.year:
                    total += float(mov.get('valor', 0))
            except: continue
    return total

# --- COMPATIBILIDADE COM VIEWS ANTIGAS (ALIASED) ---
# Isso garante que se uma View chamar 'update_orcamento' ou 'update_document', ambas funcionem.
def update_orcamento(id_doc, dados): return update_document("orcamentos", id_doc, dados)
def delete_orcamento(id_doc): return delete_document("orcamentos", id_doc)
def update_movimentacao(id_doc, dados_antigos, novos_dados): return update_document("movimentacoes", id_doc, novos_dados)
def add_movimentacao(tipo, valor, descricao, origem="Manual"):
    return add_document("movimentacoes", {
        "tipo": tipo, "valor": float(valor), "descricao": descricao, 
        "origem": origem, "data": datetime.datetime.now().isoformat()
    })

# --- FINANCEIRO ESPECÍFICO ---
def pagar_divida_fixa(divida):
    try:
        update_document("dividas", divida['id'], {'pago': True, 'data_pagamento': datetime.datetime.now().isoformat()})
        add_movimentacao("Saida", divida['valor'], f"Pgto: {divida['nome']}", "Dívidas")
        return True
    except: return False

# --- USUÁRIOS ---
def get_user_doc_by_email(email):
    users = get_collection("users")
    for u in users:
        if u.get('email') == email: return u
    return None

def verify_user_password(email, password):
    user = get_user_doc_by_email(email)
    if user:
        senha_db = str(user.get('senha') or user.get('password') or '')
        return senha_db == str(password)
    return False

# No final do seu firebase_service.py:

def get_saldo_caixa():
    transacoes = get_collection("financeiro")
    saldo = 0.0
    for t in transacoes:
        try:
            # Garante que o valor seja float mesmo se vier como string ou vírgula
            valor = float(str(t.get('valor', 0)).replace(',', '.'))
            if t.get('tipo') == 'RECEITA':
                saldo += valor
            else:
                saldo -= valor
        except: continue
    return saldo

def get_orcamentos_by_status(status):
    todos = get_collection("orcamentos")
    return [o for o in todos if o.get('status') == status]

def get_dividas_pendentes():
    transacoes = get_collection("financeiro")
    return [t for t in transacoes if t.get('tipo') == 'DESPESA' and t.get('status') != 'PAGO']

def get_receitas_pendentes():
    transacoes = get_collection("financeiro")
    return [t for t in transacoes if t.get('tipo') == 'RECEITA' and t.get('status') != 'RECEBIDO']

def get_orcamentos_finalizados_nao_pagos():
    try:
        todos = get_collection("orcamentos")
        return [o for o in todos if o.get('status') == 'FINALIZADO' and o.get('pagamento') != 'PAGO']
    except:
        return []
    
# --- ADICIONE ISSO NO FINAL DO SEU firebase_service.py ---

def get_extrato_lista():
    """Busca todas as movimentações financeiras para exibir no extrato"""
    # A sua View está chamando essa função para listar as entradas/saídas
    # Vamos buscar da coleção 'financeiro' ou 'movimentacoes' (ajuste conforme seu banco)
    try:
        dados = get_collection("financeiro")
        # Ordena por data (as mais recentes primeiro) se o campo 'data' existir
        return sorted(dados, key=lambda x: x.get('data', ''), reverse=True)
    except:
        return []

def get_orcamentos_lista():
    """Busca a lista de orçamentos para o Grid de Cards"""
    # Essa função é a que a BudgetView que refizemos vai precisar também!
    return get_collection("orcamentos")

def add_orcamento(dados):
    """Atalho para adicionar orçamento e retornar o ID (usado no popup de novo cliente)"""
    # O Firestore REST API retorna o nome do doc criado no POST
    try:
        import requests
        res = requests.post(f"{BASE_URL}/orcamentos", json=_converter_para_firestore(dados))
        if res.status_code == 200:
            id_gerado = res.json().get('name', '').split('/')[-1]
            return True, id_gerado
        return False, None
    except:
        return False, None