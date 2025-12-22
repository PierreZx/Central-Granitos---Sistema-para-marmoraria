import firebase_admin
from firebase_admin import credentials, firestore
import os

# Variável global para o banco
db = None

def initialize_firebase():
    global db
    
    if not firebase_admin._apps:
        try:
            # Pega o caminho do arquivo de chaves
            cred_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
            
            # Carrega as credenciais
            cred = credentials.Certificate(cred_path)
            
            # Inicializa APENAS o Banco de Dados (Sem Storage por enquanto)
            firebase_admin.initialize_app(cred)
            
            # Conecta ao cliente
            db = firestore.client()
            print("✅ Firebase Firestore conectado! (Modo Fotos Locais)")
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return None
    else:
        db = firestore.client()
    
    return db

if __name__ == "__main__":
    initialize_firebase()