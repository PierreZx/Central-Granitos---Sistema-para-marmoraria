import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND, AUTH_EMAIL, AUTH_PASSWORD
from src.services import firebase_service

def LoginView(page: ft.Page):
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

        # 1. Verificação de ACESSO PRODUÇÃO
        if email == "acesso.producao@gmail.com" and senha == "MarmorariaC55":
            page.session.set("user_role", "producao")
            show_snack("Bem-vindo à Área de Produção!", success=True)
            page.go("/producao") # CORRIGIDO: de push_route para go
            return

        # 2. Verificação Admin/Geral
        if email == AUTH_EMAIL and senha == AUTH_PASSWORD:
            page.session.set("user_role", "admin")
            show_snack("Login realizado com sucesso!", success=True)
            page.go("/dashboard") # CORRIGIDO: de push_route para go
        else:
            show_snack("E-mail ou senha incorretos!", success=False)

    # --- UI ---
    logo = ft.Text("CENTRAL GRANITOS", size=30, color=COLOR_PRIMARY, style=ft.TextStyle(weight="bold"))
    
    campo_usuario = ft.TextField(
        label="E-mail", height=50, border_radius=10, filled=True, 
        focused_border_color=COLOR_PRIMARY, value=AUTH_EMAIL
    )
    
    campo_senha = ft.TextField(
        label="Senha", password=True, height=50, border_radius=10, filled=True, 
        focused_border_color=COLOR_PRIMARY, can_reveal_password=True
    )

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, style=ft.TextStyle(weight="w600")),
        height=50, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=realizar_login,
    )

    return ft.Container(
        content=ft.Column([
            logo,
            ft.Text("Login Administrativo", size=18, color=ft.colors.GREY_700),
            ft.Container(height=10),
            campo_usuario,
            campo_senha,
            ft.Container(height=10),
            btn_entrar,
        ], horizontal_alignment="center", spacing=15),
        padding=40,
        width=400,
        bgcolor=COLOR_WHITE,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=15, color="#0000001A")
    )