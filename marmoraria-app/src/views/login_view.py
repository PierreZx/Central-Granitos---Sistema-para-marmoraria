import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND, AUTH_EMAIL, AUTH_PASSWORD
from src.services import firebase_service

def LoginView(page: ft.Page):
    """Tela de login corrigida para Versão 0.25.2"""

    def show_snack(msg: str, success: bool = True):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=COLOR_WHITE),
            bgcolor=ft.colors.GREEN_600 if success else ft.colors.RED_600,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def realizar_login(e):
        email = campo_usuario.value.strip()
        senha = campo_senha.value.strip()

        if not email or not senha:
            show_snack("Preencha todos os campos!", success=False)
            return

        print(f"Tentativa de login: {email}")

        # 1. Verificação de ACESSO PRODUÇÃO (Fixo)
        if email == "acesso.producao@gmail.com" and senha == "MarmorariaC55":
            page.session.set("user_role", "producao")
            show_snack("Bem-vindo à Área de Produção!", success=True)
            page.push_route("/producao")
            return

        # 2. Verificação de ADM LOCAL (O que você está tentando usar)
        if email == AUTH_EMAIL and senha == AUTH_PASSWORD:
            page.session.set("user_role", "admin")
            show_snack("Bem-vindo, Administrador!", success=True)
            page.go("/dashboard")  # <--- MUDAR PARA page.go
            return

        # 3. Verificação via FIREBASE (Caso os de cima falhem)
        try:
            if firebase_service.verify_user_password(email, senha):
                page.session.set("user_role", "admin")
                show_snack("Login realizado com sucesso!", success=True)
                page.push_route("/dashboard")
                return
        except Exception as err:
            print(f"Erro Firebase: {err}")

        # Se chegar aqui, falhou
        show_snack("E-mail ou senha incorretos!", success=False)

    # --- UI ---
    logo = ft.Text("CENTRAL GRANITOS", size=30, weight="bold", color=COLOR_PRIMARY)
    
    campo_usuario = ft.TextField(
        label="E-mail", 
        height=50, 
        border_radius=10, 
        filled=True, 
        focused_border_color=COLOR_PRIMARY,
        value=AUTH_EMAIL # Já deixa preenchido para facilitar seu teste
    )
    
    campo_senha = ft.TextField(
        label="Senha", 
        password=True, 
        height=50, 
        border_radius=10, 
        filled=True, 
        focused_border_color=COLOR_PRIMARY, 
        can_reveal_password=True
    )

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight=ft.FontWeight.W_600),
        height=50,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=realizar_login,
    )

    return ft.Container(
        content=ft.Column([
            logo,
            ft.Text("Login Administrativo", size=18, color=COLOR_PRIMARY),
            ft.Container(height=20),
            campo_usuario,
            ft.Container(height=10),
            campo_senha,
            ft.Container(height=20),
            btn_entrar,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        expand=True,
        bgcolor=COLOR_BACKGROUND
    )