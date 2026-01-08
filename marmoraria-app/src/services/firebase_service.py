import requests
import json
import os
import datetime
import socket

# --- CONFIGURAÇÕES ---
PROJECT_ID = "marmoraria-app"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# --- CONVERSORES (TRATAM O FORMATO RESTRITO DO FIREBASE) ---
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

# --- CONEXÃO E BASE ---
def verificar_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except: return False

def get_collection(collection_name):
    if not verificar_conexao(): return []
    try:
        res = requests.get(f"{BASE_URL}/{collection_name}?pageSize=300")
        if res.status_code == 200 and 'documents' in res.json():
            return [_converter_de_firestore(doc) for doc in res.json()['documents']]
        return []
    except: return []

def add_document(collection, dados):
    try:
        res = requests.post(f"{BASE_URL}/{collection}", json=_converter_para_firestore(dados))
        return res.status_code == 200
    except: return False

def update_document(collection, doc_id, dados):
    try:
        corpo_json = _converter_para_firestore(dados)
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        url = f"{BASE_URL}/{collection}/{doc_id}?{mask}"
        res = requests.patch(url, json=corpo_json)
        return res.status_code == 200
    except: return False

def delete_document(collection, doc_id):
    try:
        res = requests.delete(f"{BASE_URL}/{collection}/{doc_id}")
        return res.status_code == 200
    except: return False

# --- FINANCEIRO (USADO PELA FINANCIAL_VIEW) ---

def get_saldo_caixa():
    """Calcula saldo real baseado no extrato (Entradas - Saídas)"""
    movs = get_collection("financeiro")
    saldo = 0.0
    for m in movs:
        try:
            # Pega valor independente de ser Entrada/Receita ou Saida/Despesa
            v = float(str(m.get('valor', 0)).replace(',', '.'))
            tipo = str(m.get('tipo', '')).upper()
            if tipo in ['ENTRADA', 'RECEITA']: saldo += v
            elif tipo in ['SAIDA', 'DESPESA']: saldo -= v
        except: continue
    return saldo

def get_dividas_pendentes():
    """Busca contas a pagar (DESPESAS não pagas)"""
    dados = get_collection("financeiro")
    return [d for d in dados if str(d.get('tipo', '')).upper() in ['SAIDA', 'DESPESA'] and d.get('status') != 'Pago']

def get_extrato_lista():
    """Lista todas as movimentações para a aba de extrato"""
    dados = get_collection("financeiro")
    # Ordena por data (mais recente primeiro)
    return sorted(dados, key=lambda x: x.get('data', x.get('data_vencimento', '')), reverse=True)

def add_divida_fixa(dados):
    """Cria um agendamento de conta a pagar"""
    dados['tipo'] = 'Saida'
    if 'status' not in dados: dados['status'] = 'Pendente'
    return add_document("financeiro", dados)

def add_movimentacao(tipo, valor, descricao, origem="Manual"):
    """Cria um registro direto no extrato"""
    dados = {
        "tipo": tipo,
        "valor": float(str(valor).replace(',', '.')),
        "descricao": descricao,
        "origem": origem,
        "data": datetime.datetime.now().isoformat(),
        "status": "Pago" if tipo == "Saida" else "Recebido"
    }
    return add_document("financeiro", dados)

def pagar_divida_fixa(item):
    """Dá baixa em uma conta a pagar e gera o extrato"""
    item['status'] = 'Pago'
    item['data_pagamento'] = datetime.datetime.now().isoformat()
    # Atualiza o documento original
    update_document("financeiro", item['id'], item)
    return True

def delete_divida_fixa(id_doc):
    return delete_document("financeiro", id_doc)

# --- ORÇAMENTOS (USADO PELA BUDGET_VIEW) ---

def get_orcamentos_lista():
    return get_collection("orcamentos")

def get_orcamentos_finalizados_nao_pagos():
    """Para a aba 'Contas a Receber' do Financeiro"""
    todos = get_collection("orcamentos")
    return [o for o in todos if o.get('status') == 'Finalizado' and not o.get('pago')]

def add_orcamento(dados):
    """Cria orçamento e retorna (Sucesso, ID)"""
    try:
        res = requests.post(f"{BASE_URL}/orcamentos", json=_converter_para_firestore(dados))
        if res.status_code == 200:
            return True, res.json().get('name', '').split('/')[-1]
        return False, None
    except: return False, None

def receber_orcamento(item):
    """Marca orçamento como pago e gera entrada no financeiro"""
    item['pago'] = True
    item['status_pagamento'] = 'Pago'
    update_document("orcamentos", item['id'], item)
    # Registra a entrada no financeiro
    return add_movimentacao("Entrada", item.get('total_geral', 0), f"Receb. Orç: {item.get('cliente_nome')}", "Vendas")

# --- USUÁRIOS E LOGIN ---
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

def initialize_firebase(): return True