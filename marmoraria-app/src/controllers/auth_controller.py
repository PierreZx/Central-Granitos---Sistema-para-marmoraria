from src.services import firebase_service
from src.config import AUTH_EMAIL, AUTH_PASSWORD

class AuthController:
    
    @staticmethod
    def autenticar(email, senha):
        """
        Retorna: (Sucesso: bool, Mensagem: str)
        """
        email = email.strip().lower()
        
        # 1. Tenta Firebase (Prioridade)
        try:
            firebase_service.initialize_firebase()
            if firebase_service.verify_user_password(email, senha):
                return True, "Login realizado via Banco de Dados!"
        except Exception as e:
            print(f"Erro conexão Firebase: {e}")

        # 2. Fallback (Login de Emergência definido no config.py)
        # Útil se a internet cair ou o banco falhar
        if email == AUTH_EMAIL.lower() and senha == AUTH_PASSWORD:
            # Aproveita para tentar criar esse usuário no banco para a próxima vez
            firebase_service.create_user_firestore(AUTH_EMAIL, AUTH_PASSWORD)
            return True, "Login Mestre (Local) realizado!"

        return False, "Usuário ou senha incorretos."