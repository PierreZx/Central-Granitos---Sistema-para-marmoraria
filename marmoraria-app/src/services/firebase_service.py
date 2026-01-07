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
        if v is None: fields[k] = {"nullValue": None}
        elif isinstance(v, bool): fields[k] = {"booleanValue": v}
        elif isinstance(v, int): fields[k] = {"integerValue": str(v)}
        elif isinstance(v, float): fields[k] = {"doubleValue": v}
        elif isinstance(v, list):
            vals = [{"stringValue": str(i)} for i in v]
            fields[k] = {"arrayValue": {"values": vals}}
        else: fields[k] = {"stringValue": str(v)}
    return {"fields": fields}

def _converter_de_firestore(doc):
    name = doc.get('name', '')
    obj = {'id': name.split('/')[-1] if name else 'unknown'}
    if 'fields' in doc:
        for k, v in doc['fields'].items():
            # Pega o primeiro valor encontrado no dict (stringValue, integerValue, etc)
            val = list(v.values())[0]
            if 'integerValue' in v: val = int(val)
            if 'doubleValue' in v: val = float(val)
            if 'arrayValue' in v: # Se for lista
                val = [list(x.values())[0] for x in v['arrayValue'].get('values', [])]
            obj[k] = val
    return obj

# --- FUNÇÕES BÁSICAS ---
def initialize_firebase():
    print(f"🔥 Serviço Firebase REST iniciado")
    return True

def verificar_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# --- UTILITÁRIOS GERAIS ---
def get_collection_count(collection):
    """Conta quantos documentos existem em uma coleção"""
    if not verificar_conexao(): return 0
    try:
        res = requests.get(f"{BASE_URL}/{collection}")
        if res.status_code == 200 and 'documents' in res.json():
            return len(res.json()['documents'])
        return 0
    except: return 0

def get_pendencias_count():
    """Retorna 0 pois estamos operando em modo online/web"""
    return 0

def sincronizar_agora():
    """Simula sincronização"""
    return True, "Sincronizado (Modo Online)"

# --- ORÇAMENTOS ---
def get_orcamentos_lista():
    lista = []
    if verificar_conexao():
        try:
            res = requests.get(f"{BASE_URL}/orcamentos?pageSize=100")
            if res.status_code == 200 and 'documents' in res.json():
                for doc in res.json()['documents']:
                    lista.append(_converter_de_firestore(doc))
        except: pass
    # Ordena por data (se houver campo data_criacao)
    lista.sort(key=lambda x: x.get('data_criacao', ''), reverse=True)
    return lista

def add_orcamento(dados, forcar_online=False):
    if not verificar_conexao(): return False, "Sem internet"
    try:
        if 'data_criacao' not in dados: dados['data_criacao'] = datetime.datetime.now().isoformat()
        if 'status' not in dados: dados['status'] = 'Em Aberto'
        
        res = requests.post(f"{BASE_URL}/orcamentos", json=_converter_para_firestore(dados))
        if res.status_code == 200: return True, res.json()['name'].split('/')[-1]
        return False, res.text
    except Exception as e: return False, str(e)

def update_orcamento(id_doc, dados):
    if not verificar_conexao(): return False, "Sem internet"
    try:
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        res = requests.patch(f"{BASE_URL}/orcamentos/{id_doc}?{mask}", json=_converter_para_firestore(dados))
        return (res.status_code == 200), res.text
    except Exception as e: return False, str(e)

def delete_orcamento(id_doc):
    if not verificar_conexao(): return False
    try:
        requests.delete(f"{BASE_URL}/orcamentos/{id_doc}")
        return True
    except: return False

def get_orcamentos_finalizados_nao_pagos():
    todos = get_orcamentos_lista()
    # Filtra: Status Finalizado E (não tem campo 'pago' OU 'pago' é falso)
    return [o for o in todos if o.get('status') == 'Finalizado' and not o.get('pago_financeiro', False)]

def receber_orcamento(orc):
    """Marca orçamento como pago e cria entrada no caixa"""
    try:
        # 1. Marca como pago
        update_orcamento(orc['id'], {'pago_financeiro': True, 'data_pagamento': datetime.datetime.now().isoformat()})
        
        # 2. Adiciona no caixa
        add_movimentacao(
            tipo="Entrada",
            valor=float(orc.get('total_geral', 0)),
            descricao=f"Recebimento: {orc.get('cliente_nome')}",
            origem="Orçamento"
        )
        return True
    except: return False

def repor_estoque_devolucao(orc):
    """(Simplificado) Apenas logica placeholder, pois exigiria saber quais chapas exatas"""
    print(f"Devolução simulada para orçamento {orc.get('id')}")
    return True

# --- ESTOQUE ---
def get_estoque_lista():
    if not verificar_conexao(): return []
    try:
        res = requests.get(f"{BASE_URL}/estoque?pageSize=100")
        lista = []
        if res.status_code == 200 and 'documents' in res.json():
            for doc in res.json()['documents']:
                lista.append(_converter_de_firestore(doc))
        return lista
    except: return []

def add_item_estoque(dados):
    if not verificar_conexao(): return False, "Sem internet"
    try:
        dados['created_at'] = datetime.datetime.now().isoformat()
        res = requests.post(f"{BASE_URL}/estoque", json=_converter_para_firestore(dados))
        return (res.status_code == 200), res.text
    except Exception as e: return False, str(e)

def update_item_estoque(item_id, dados):
    if not verificar_conexao(): return False
    try:
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        requests.patch(f"{BASE_URL}/estoque/{item_id}?{mask}", json=_converter_para_firestore(dados))
        return True, "Ok"
    except Exception as e: return False, str(e)

def delete_item_estoque(item_id):
    if not verificar_conexao(): return False
    try:
        requests.delete(f"{BASE_URL}/estoque/{item_id}")
        return True, "Ok"
    except Exception as e: return False, str(e)

def descontar_estoque_producao(orc):
    """Mock para Web"""
    return True, "Estoque atualizado"

# --- FINANCEIRO ---
def get_extrato_lista():
    lista = []
    if verificar_conexao():
        try:
            res = requests.get(f"{BASE_URL}/movimentacoes?pageSize=50") # Limite para não pesar
            if res.status_code == 200 and 'documents' in res.json():
                for doc in res.json()['documents']:
                    lista.append(_converter_de_firestore(doc))
        except: pass
    lista.sort(key=lambda x: x.get('data', ''), reverse=True)
    return lista

def get_saldo_caixa():
    """Calcula saldo somando entradas e subtraindo saídas"""
    extrato = get_extrato_lista()
    saldo = 0.0
    for mov in extrato:
        val = float(mov.get('valor', 0))
        if mov.get('tipo') == 'Entrada': saldo += val
        else: saldo -= val
    return saldo

def get_faturamento_mes_atual():
    extrato = get_extrato_lista()
    agora = datetime.datetime.now()
    total = 0.0
    for mov in extrato:
        if mov.get('tipo') == 'Entrada':
            try:
                data_mov = datetime.datetime.fromisoformat(mov.get('data', ''))
                if data_mov.month == agora.month and data_mov.year == agora.year:
                    total += float(mov.get('valor', 0))
            except: pass
    return total

def add_movimentacao(tipo, valor, descricao, origem="Manual"):
    dados = {
        "tipo": tipo, "valor": float(valor), "descricao": descricao, 
        "origem": origem, "data": datetime.datetime.now().isoformat()
    }
    if not verificar_conexao(): return False
    try:
        requests.post(f"{BASE_URL}/movimentacoes", json=_converter_para_firestore(dados))
        return True
    except: return False

def update_movimentacao(mov_id, dados_antigos, novos_dados):
    if not verificar_conexao(): return False
    try:
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in novos_dados.keys()])
        requests.patch(f"{BASE_URL}/movimentacoes/{mov_id}?{mask}", json=_converter_para_firestore(novos_dados))
        return True
    except: return False

def delete_movimentacao(mov_id, mov_dados):
    if not verificar_conexao(): return False
    try:
        requests.delete(f"{BASE_URL}/movimentacoes/{mov_id}")
        return True
    except: return False

# --- DÍVIDAS ---
def get_dividas_pendentes():
    lista = []
    if verificar_conexao():
        try:
            res = requests.get(f"{BASE_URL}/dividas")
            if res.status_code == 200 and 'documents' in res.json():
                for doc in res.json()['documents']:
                    d = _converter_de_firestore(doc)
                    if not d.get('pago', False): # Apenas não pagas
                        lista.append(d)
        except: pass
    return lista

def add_divida_fixa(dados):
    dados['pago'] = False
    dados['criado_em'] = datetime.datetime.now().isoformat()
    if not verificar_conexao(): return False
    try:
        requests.post(f"{BASE_URL}/dividas", json=_converter_para_firestore(dados))
        return True
    except: return False

def update_divida_fixa(divida_id, dados):
    if not verificar_conexao(): return False
    try:
        mask = "&".join([f"updateMask.fieldPaths={k}" for k in dados.keys()])
        requests.patch(f"{BASE_URL}/dividas/{divida_id}?{mask}", json=_converter_para_firestore(dados))
        return True
    except: return False

def delete_divida_fixa(divida_id):
    if not verificar_conexao(): return False
    try:
        requests.delete(f"{BASE_URL}/dividas/{divida_id}")
        return True
    except: return False

def pagar_divida_fixa(divida):
    """Marca como pago e lança saída no caixa"""
    try:
        # 1. Atualiza dívida para paga
        update_divida_fixa(divida['id'], {'pago': True, 'data_pagamento': datetime.datetime.now().isoformat()})
        # 2. Lança saída no caixa
        add_movimentacao("Saida", divida['valor'], f"Pgto: {divida['nome']}", "Dívidas")
        return True
    except: return False

# --- USUÁRIOS E LOGIN ---
def get_user_doc_by_email(email):
    if not verificar_conexao(): return None
    try:
        res = requests.get(f"{BASE_URL}/users")
        if res.status_code == 200 and 'documents' in res.json():
            for doc in res.json()['documents']:
                u = _converter_de_firestore(doc)
                if u.get('email') == email: return u
        return None
    except: return None

def verify_user_password(email, password):
    """Verifica se o usuário existe e a senha bate"""
    if not verificar_conexao(): return False
    try:
        user = get_user_doc_by_email(email)
        if user:
            senha_db = str(user.get('senha') or user.get('password') or '')
            if senha_db == str(password):
                return True
        return False
    except: return False