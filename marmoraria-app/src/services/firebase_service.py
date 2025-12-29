import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter # <--- IMPORTANTE: Importar isso
from pathlib import Path
import hashlib

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