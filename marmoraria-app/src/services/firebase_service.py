import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter # <--- IMPORTANTE: Importar isso
from pathlib import Path
import hashlib
import math

db = None

def initialize_firebase():
    global db
    if db is not None:
        return db

    try:
        base_path = Path(__file__).resolve().parent.parent.parent
        cred_path = base_path / "serviceAccountKey.json"
        
        print(f"🔍 Procurando chave em: {cred_path}")

        if not cred_path.exists():
            print("❌ ERRO CRÍTICO: O arquivo serviceAccountKey.json não foi encontrado!")
            return None

        cred = credentials.Certificate(str(cred_path))
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("✅ Firebase Conectado com Sucesso!")
        return db

    except Exception as e:
        print(f"❌ Falha na conexão com Firebase: {e}")
        return None

# --- Usuários ---

def get_user_doc_by_email(email: str):
    if not db: initialize_firebase()
    if not db: return None

    try:
        users_ref = db.collection('users')
        # CORREÇÃO: Usando FieldFilter no lugar de argumentos posicionais
        query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1).get()
        if not query:
            return None
        return query[0].to_dict()
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def verify_user_password(email: str, password: str) -> bool:
    try:
        user = get_user_doc_by_email(email)
        if not user:
            return False
        stored_hash = user.get('password_hash')
        if not stored_hash:
            return user.get('password') == password
        check_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return stored_hash == check_hash
    except Exception:
        return False

def create_user_firestore(email: str, password: str) -> bool:
    if not db: initialize_firebase()
    if not db: return False

    try:
        if get_user_doc_by_email(email):
            return True 

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        db.collection('users').add({
            'email': email, 
            'password_hash': password_hash,
            'role': 'admin'
        })
        print(f"✅ Usuário {email} criado no banco.")
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False

# --- Estoque ---

def add_item_estoque(dados: dict):
    global db
    if not db: initialize_firebase()
    try:
        dados['created_at'] = firestore.SERVER_TIMESTAMP
        db.collection('estoque').add(dados)
        return True, "Item adicionado com sucesso!"
    except Exception as e:
        return False, f"Erro: {e}"

def get_estoque_lista():
    global db
    if not db: initialize_firebase()
    try:
        docs = db.collection('estoque').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        items = []
        for doc in docs:
            item = doc.to_dict()
            item['id'] = doc.id 
            items.append(item)
        return items
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return []

def update_item_estoque(item_id: str, dados: dict):
    global db
    if not db: initialize_firebase()
    try:
        db.collection('estoque').document(item_id).update(dados)
        return True, "Item atualizado!"
    except Exception as e:
        return False, f"Erro: {e}"

def delete_item_estoque(item_id: str):
    global db
    if not db: initialize_firebase()
    try:
        db.collection('estoque').document(item_id).delete()
        return True, "Item removido!"
    except Exception as e:
        return False, f"Erro: {e}"

# --- Utils Gerais ---

def get_collection_count(collection_name: str) -> int:
    global db
    if db is None:
        initialize_firebase()
    try:
        collection_ref = db.collection(collection_name)
        count_query = collection_ref.count()
        results = count_query.get()
        return results[0][0].value
    except Exception as e:
        return 0
    
def get_orcamentos_lista():
    """Retorna lista de todos os orçamentos"""
    try:
        docs = db.collection("orcamentos").stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            lista.append(d)
        return lista
    except Exception as e:
        print(f"Erro ao buscar orçamentos: {e}")
        return []

def add_orcamento(dados):
    """Cria um novo orçamento"""
    try:
        # Adiciona data de criação se não tiver
        from datetime import datetime
        dados['data_criacao'] = datetime.now().isoformat()
        dados['status'] = 'Em Aberto' # Status inicial
        
        doc_ref = db.collection("orcamentos").add(dados)
        return True, doc_ref[1].id # Retorna Sucesso e o ID gerado
    except Exception as e:
        return False, str(e)

def update_orcamento(id_doc, dados):
    """Atualiza um orçamento existente (adicionar peças, mudar status)"""
    try:
        db.collection("orcamentos").document(id_doc).update(dados)
        return True, "Atualizado com sucesso"
    except Exception as e:
        return False, str(e)

def delete_orcamento(id_doc):
    """Remove um orçamento"""
    try:
        db.collection("orcamentos").document(id_doc).delete()
        return True
    except Exception as e:
        return False
    
def descontar_estoque_producao(orcamento):
    """
    Desconta a metragem das pedras usadas no orçamento diretamente do estoque.
    Recalcula a quantidade de chapas baseado na média atual.
    """
    try:
        itens = orcamento.get('itens', [])
        
        # Agrupa consumo por Pedra ID (caso tenha várias peças da mesma pedra)
        consumo_por_pedra = {} 
        
        for item in itens:
            cfg = item.get('config', {})
            pedra_id = cfg.get('pedra_id')
            area_peca = float(item.get('area', 0))
            
            if pedra_id and area_peca > 0:
                if pedra_id in consumo_por_pedra:
                    consumo_por_pedra[pedra_id] += area_peca
                else:
                    consumo_por_pedra[pedra_id] = area_peca
        
        # Atualiza no Banco
        for p_id, area_gasta in consumo_por_pedra.items():
            doc_ref = db.collection("estoque").document(p_id)
            doc = doc_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                metros_atuais = float(dados.get('metros', 0) or 0)
                qtd_atual = int(dados.get('quantidade', 0) or 0)
                
                # 1. Calcula a média de tamanho por chapa (para saber qts baixar)
                # Se não tiver dados, assume uma chapa padrão de 5m² para não dar erro
                media_por_chapa = (metros_atuais / qtd_atual) if qtd_atual > 0 else 5.0
                
                # 2. Desconta os metros
                novos_metros = metros_atuais - area_gasta
                
                # 3. Recalcula quantidade de chapas (arredondando para cima)
                # Ex: Se sobrou 2.1m e a chapa média é 2m, considera 2 chapas (uma inteira e um retalho grande)
                # Ou se preferir arredondamento matemático simples, usamos round. 
                # Aqui usaremos ceil (teto) para ser conservador: se tem pedra, conta como chapa/retalho.
                nova_qtd = math.ceil(novos_metros / media_por_chapa) if novos_metros > 0 else 0
                
                # Atualiza
                doc_ref.update({
                    "metros": f"{novos_metros:.2f}", # Salva como string formatada ou float, conforme seu padrão
                    "quantidade": str(nova_qtd)
                })
                print(f"Estoque atualizado: -{area_gasta}m² na pedra {dados.get('nome')}")
                
        return True, "Estoque atualizado com sucesso!"
        
    except Exception as e:
        print(f"Erro ao baixar estoque: {e}")
        return False, str(e)
    
def repor_estoque_devolucao(orcamento):
    """
    Estorna (devolve) a metragem das pedras para o estoque quando um orçamento é cancelado/retornado.
    """
    try:
        itens = orcamento.get('itens', [])
        devolucao_por_pedra = {} 
        
        # Soma tudo que tem que devolver
        for item in itens:
            cfg = item.get('config', {})
            pedra_id = cfg.get('pedra_id')
            area_peca = float(item.get('area', 0))
            
            if pedra_id and area_peca > 0:
                if pedra_id in devolucao_por_pedra:
                    devolucao_por_pedra[pedra_id] += area_peca
                else:
                    devolucao_por_pedra[pedra_id] = area_peca
        
        # Atualiza no Banco
        for p_id, area_volta in devolucao_por_pedra.items():
            doc_ref = db.collection("estoque").document(p_id)
            doc = doc_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                metros_atuais = float(dados.get('metros', 0) or 0)
                qtd_atual = int(dados.get('quantidade', 0) or 0)
                
                # Evita divisão por zero para achar a média
                media_por_chapa = (metros_atuais / qtd_atual) if qtd_atual > 0 else 5.0
                
                # SOMA de volta (Estorno)
                novos_metros = metros_atuais + area_volta
                
                # Recalcula chapas
                # Usa math.ceil para arredondar pra cima (se tem pedra, conta como chapa/retalho)
                import math
                nova_qtd = math.ceil(novos_metros / media_por_chapa) if media_por_chapa > 0 else 0
                
                doc_ref.update({
                    "metros": f"{novos_metros:.2f}",
                    "quantidade": str(nova_qtd)
                })
                
        return True, "Estoque estornado com sucesso!"
        
    except Exception as e:
        print(f"Erro ao estornar estoque: {e}")
        return False, str(e)