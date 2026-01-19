import requests
import json
import os
import datetime
import socket

# --- CONFIGURAÇÕES ---
PROJECT_ID = "marmoraria-app"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# --- CONVERSORES ---
def _converter_para_firestore(dados):
    fields = {}
    for k, v in dados.items():
        if v is None:
            fields[k] = {"nullValue": None}
        elif isinstance(v, bool):
            fields[k] = {"booleanValue": v}
        elif isinstance(v, int):
            fields[k] = {"integerValue": str(v)}
        elif isinstance(v, float):
            fields[k] = {"doubleValue": v}
        elif isinstance(v, list):
            vals = []
            for item in v:
                if isinstance(item, dict):
                    vals.append({"mapValue": _converter_para_firestore(item)})
                else:
                    vals.append({"stringValue": str(item)})
            fields[k] = {"arrayValue": {"values": vals}}
        elif isinstance(v, dict):
            fields[k] = {"mapValue": _converter_para_firestore(v)}
        else:
            fields[k] = {"stringValue": str(v)}
    return {"fields": fields}

def _extrair_valor(v):
    if 'stringValue' in v: return v['stringValue']
    if 'integerValue' in v: return int(v['integerValue'])
    if 'doubleValue' in v: return float(v['doubleValue'])
    if 'booleanValue' in v: return v['booleanValue']
    if 'nullValue' in v: return None
    if 'arrayValue' in v:
        return [_extrair_valor(x) for x in v['arrayValue'].get('values', [])]
    if 'mapValue' in v:
        res = {}
        for k, v2 in v['mapValue'].get('fields', {}).items():
            res[k] = _extrair_valor(v2)
        return res
    return None

def _converter_de_firestore(doc):
    name = doc.get("name", "")
    obj = {"id": name.split("/")[-1]}
    for k, v in doc.get("fields", {}).items():
        obj[k] = _extrair_valor(v)
    return obj

def get_document(collection, doc_id):
    if not verificar_conexao():
        return None
    try:
        res = requests.get(f"{BASE_URL}/{collection}/{doc_id}")
        if res.status_code == 200:
            return _converter_de_firestore(res.json())
        return None
    except Exception as e:
        print(f"Erro ao buscar documento {collection}/{doc_id}: {e}")
        return None

# --- CONEXÃO ---
def verificar_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# --- BASE CRUD ---
def get_collection(collection):
    if not verificar_conexao(): return []
    try:
        res = requests.get(f"{BASE_URL}/{collection}?pageSize=300")
        if res.status_code == 200 and "documents" in res.json():
            return [_converter_de_firestore(d) for d in res.json()["documents"]]
        return []
    except:
        return []

def add_document(collection, dados):
    try:
        res = requests.post(f"{BASE_URL}/{collection}", json=_converter_para_firestore(dados))
        return res.status_code == 200
    except:
        return False

def update_document(collection, doc_id, dados):
    try:
        corpo = _converter_para_firestore(dados)
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        url = f"{BASE_URL}/{collection}/{doc_id}?{mask}"
        res = requests.patch(url, json=corpo)
        return res.status_code == 200
    except:
        return False

def delete_document(collection, doc_id):
    try:
        res = requests.delete(f"{BASE_URL}/{collection}/{doc_id}")
        return res.status_code == 200
    except:
        return False

# =========================================================
# ====================== FINANCEIRO =======================
# =========================================================

def get_saldo_caixa():
    movs = get_collection("financeiro")
    saldo = 0.0
    for m in movs:
        try:
            v = float(str(m.get("valor", 0)).replace(",", "."))
            tipo = str(m.get("tipo", "")).upper()
            if tipo in ["ENTRADA", "RECEITA"]:
                saldo += v
            elif tipo in ["SAIDA", "DESPESA"]:
                saldo -= v
        except:
            pass
    return saldo

def get_dividas_pendentes():
    dados = get_collection("financeiro")
    return [
        d for d in dados
        if str(d.get("tipo", "")).upper() in ["SAIDA", "DESPESA"]
        and d.get("status") != "Pago"
    ]

def get_extrato_lista():
    dados = get_collection("financeiro")
    return sorted(dados, key=lambda x: x.get("data", ""), reverse=True)

def add_divida_fixa(dados):
    dados["tipo"] = "Saida"
    if "status" not in dados:
        dados["status"] = "Pendente"
    return add_document("financeiro", dados)

def pagar_divida_fixa(item):
    item["status"] = "Pago"
    item["data_pagamento"] = datetime.datetime.now().isoformat()
    return update_document("financeiro", item["id"], item)

def delete_divida_fixa(id_doc):
    return delete_document("financeiro", id_doc)

# ✅ NOVO: editar dívida
def update_divida_fixa(id_doc, dados):
    return update_document("financeiro", id_doc, dados)

def add_movimentacao(tipo, valor, descricao, origem="Manual"):
    dados = {
        "tipo": tipo,
        "valor": float(str(valor).replace(",", ".")),
        "descricao": descricao,
        "origem": origem,
        "data": datetime.datetime.now().isoformat(),
        "status": "Pago" if tipo == "Saida" else "Recebido"
    }
    return add_document("financeiro", dados)

# ✅ NOVO: editar extrato
def update_movimentacao(id_doc, dados):
    return update_document("financeiro", id_doc, dados)

# ✅ NOVO: apagar extrato
def delete_movimentacao(id_doc):
    return delete_document("financeiro", id_doc)

# =========================================================
# ===================== ORÇAMENTOS ========================
# =========================================================

def get_orcamentos_lista():
    return get_collection("orcamentos")

def get_orcamentos_finalizados_nao_pagos():
    todos = get_collection("orcamentos")
    return [o for o in todos if o.get("status") == "Finalizado" and not o.get("pago")]

def receber_orcamento(item):
    item["pago"] = True
    item["status_pagamento"] = "Pago"
    item["status"] = "Finalizado" # Garante que o status mude no card
    update_document("orcamentos", item["id"], item)
    
    # O valor deve vir do total_geral calculado na nova calculadora
    valor_total = float(str(item.get("total_geral", 0)).replace(",", "."))
    
    return add_movimentacao(
        "Entrada",
        valor_total,
        f"Receb. Orç: {item.get('cliente_nome')}",
        "Vendas"
    )

# =========================================================
# =================== USUÁRIOS / LOGIN ====================
# =========================================================

def get_user_doc_by_email(email):
    users = get_collection("users")
    for u in users:
        if u.get("email") == email:
            return u
    return None

def verify_user_password(email, password):
    user = get_user_doc_by_email(email)
    if user:
        senha_db = str(user.get("senha") or user.get("password") or "")
        return senha_db == str(password)
    return False

def initialize_firebase():
    return True

def get_collection_count(collection):
    try:
        return len(get_collection(collection))
    except:
        return 0

def get_orcamentos_by_status(status):
    """Busca orçamentos filtrados pelo status (PENDENTE, PRODUZINDO, etc)"""
    todos = get_collection("orcamentos")
    # Filtra a lista localmente, já que estamos usando a API REST simples
    return [o for o in todos if o.get("status") == status]