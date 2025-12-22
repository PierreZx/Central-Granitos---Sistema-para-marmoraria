import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import hashlib

# Variável global para manter a conexão viva
db = None

def initialize_firebase():
    global db
    
    # Se já estiver conectado, não faz nada e devolve o banco
    if db is not None:
        return db

    try:
        # --- A MÁGICA DO CAMINHO CORRETO ---
        # __file__ é este arquivo. .parent sobe pastas.
        # src/services -> src -> raiz do projeto
        base_path = Path(__file__).resolve().parent.parent.parent
        cred_path = base_path / "serviceAccountKey.json"
        
        print(f"🔍 Procurando chave em: {cred_path}")

        if not cred_path.exists():
            print("❌ ERRO CRÍTICO: O arquivo serviceAccountKey.json não foi encontrado!")
            return None

        # Carrega as credenciais
        cred = credentials.Certificate(str(cred_path))
        
        # Inicializa o app se ainda não existir
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("✅ Firebase Conectado com Sucesso!")
        return db

    except Exception as e:
        print(f"❌ Falha na conexão com Firebase: {e}")
        return None

# --- Funções Úteis para o Backend ---

def get_user_doc_by_email(email: str):
    """Busca usuário pelo email."""
    if not db: initialize_firebase()
    if not db: return None # Se falhar a conexão

    try:
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).get()
        if not query:
            return None
        return query[0].to_dict()
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def verify_user_password(email: str, password: str) -> bool:
    """Verifica senha hashada."""
    try:
        user = get_user_doc_by_email(email)
        if not user:
            return False
            
        stored_hash = user.get('password_hash')
        if not stored_hash:
            # Fallback para senhas antigas sem hash (se houver)
            return user.get('password') == password

        check_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return stored_hash == check_hash
    except Exception:
        return False

def create_user_firestore(email: str, password: str) -> bool:
    """Cria usuário admin se não existir."""
    if not db: initialize_firebase()
    if not db: return False

    try:
        # Verifica duplicidade
        if get_user_doc_by_email(email):
            return True # Já existe, sucesso.

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
    
    # ... (todo o código anterior continua igual)

def get_collection_count(collection_name: str) -> int:
    """Conta quantos documentos existem em uma coleção (Ex: 'estoque', 'orcamentos')."""
    global db
    if db is None:
        initialize_firebase()
    
    try:
        # Nota: O count() do Firestore é eficiente e barato
        # Ele conta no servidor sem baixar os dados todos
        collection_ref = db.collection(collection_name)
        count_query = collection_ref.count()
        results = count_query.get()
        return results[0][0].value
    except Exception as e:
        print(f"Erro ao contar coleção {collection_name}: {e}")
        return 0

def get_recent_documents(collection_name: str, limit=5, order_by="data_criacao"):
    """Pega os últimos 5 itens para mostrar nas tabelas"""
    global db
    if db is None: return []
    
    try:
        # Tenta buscar ordenado (pode precisar criar índice no Firebase depois)
        # Por enquanto, pegamos simples
        docs = db.collection(collection_name).limit(limit).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar recentes: {e}")
        return []
    
def add_item_estoque(dados: dict):
    """Adiciona uma nova chapa ao Firestore"""
    global db
    if not db: initialize_firebase()
    
    try:
        # Adiciona data de criação para ordenar depois
        dados['created_at'] = firestore.SERVER_TIMESTAMP
        db.collection('estoque').add(dados)
        return True, "Item adicionado com sucesso!"
    except Exception as e:
        print(f"Erro ao adicionar: {e}")
        return False, f"Erro: {e}"

def get_estoque_lista():
    """Busca todas as chapas e retorna uma lista de dicionários (incluindo o ID)"""
    global db
    if not db: initialize_firebase()
    
    try:
        docs = db.collection('estoque').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        items = []
        for doc in docs:
            item = doc.to_dict()
            item['id'] = doc.id # Importante para poder editar/apagar depois
            items.append(item)
        return items
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return []

def update_item_estoque(item_id: str, dados: dict):
    """Atualiza os dados de uma chapa existente"""
    global db
    if not db: initialize_firebase()
    
    try:
        db.collection('estoque').document(item_id).update(dados)
        return True, "Item atualizado!"
    except Exception as e:
        return False, f"Erro: {e}"

def delete_item_estoque(item_id: str):
    """Remove uma chapa do banco"""
    global db
    if not db: initialize_firebase()
    
    try:
        db.collection('estoque').document(item_id).delete()
        return True, "Item removido!"
    except Exception as e:
        return False, f"Erro: {e}"