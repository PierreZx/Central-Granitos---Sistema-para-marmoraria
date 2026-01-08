import flet as ft
from src.config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, 
    COLOR_BACKGROUND, AUTH_EMAIL, AUTH_PASSWORD, COLOR_TEXT
)
from src.services import firebase_service

def LoginView(page: ft.Page):
    # Ajuste de layout da página para centralizar o card de login
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def show_snack(msg: str, success: bool = True):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=COLOR_WHITE, weight="w500"),
            bgcolor=ft.colors.GREEN_600 if success else ft.colors.RED_600,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=20,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def realizar_login(e):
        # Feedback visual de carregamento
        btn_entrar.disabled = True
        btn_entrar.content = ft.ProgressRing(width=20, height=20, color=COLOR_WHITE, stroke_width=2)
        page.update()

        email = campo_usuario.value.strip()
        senha = campo_senha.value.strip()

        if not email or not senha:
            show_snack("Por favor, preencha todos os campos!", success=False)
            reset_button()
            return

        # 1. Verificação de ACESSO PRODUÇÃO
        if email == "acesso.producao@gmail.com" and senha == "MarmorariaC55":
            page.session.set("user_role", "producao")
            show_snack("Bem-vindo à Área de Produção!")
            page.go("/producao")
            return

        # 2. Verificação Admin/Geral
        if email == AUTH_EMAIL and senha == AUTH_PASSWORD:
            page.session.set("user_role", "admin")
            show_snack("Acesso autorizado. Bem-vindo!")
            page.go("/dashboard")
        else:
            show_snack("E-mail ou senha inválidos.", success=False)
            reset_button()

    def reset_button():
        btn_entrar.disabled = False
        btn_entrar.content = ft.Text("Entrar", size=16, weight="bold")
        page.update()

    # --- UI COMPONENTS ---
    
    logo_icon = ft.Container(
        content=ft.Icon(ft.icons.PRECISION_MANUFACTURING_ROUNDED, color=COLOR_PRIMARY, size=40),
        bgcolor=f"{COLOR_PRIMARY}15",
        padding=15,
        border_radius=15,
    )

    titulo = ft.Column([
        ft.Text("CENTRAL GRANITOS", size=24, weight="bold", color=COLOR_PRIMARY, letter_spacing=1),
        ft.Text("Sistema de Gestão Interna", size=14, color=ft.colors.GREY_600),
    ], horizontal_alignment="center", spacing=2)

    campo_usuario = ft.TextField(
        label="E-mail",
        hint_text="seu@email.com",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        border_radius=12,
        filled=True,
        bgcolor=ft.colors.GREY_50,
        focused_border_color=COLOR_PRIMARY,
        value=AUTH_EMAIL, # Facilitador para desenvolvimento
        on_submit=realizar_login
    )
    
    campo_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        border_radius=12,
        filled=True,
        bgcolor=ft.colors.GREY_50,
        focused_border_color=COLOR_PRIMARY,
        on_submit=realizar_login
    )

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight="bold"),
        height=55,
        style=ft.ButtonStyle(
            color=COLOR_WHITE,
            bgcolor=COLOR_PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation={"pressed": 0, "": 2},
        ),
        on_click=realizar_login,
        width=float("inf")
    )

    # Card Principal de Login
    return ft.Container(
        content=ft.Column([
            logo_icon,
            titulo,
            ft.Container(height=10),
            campo_usuario,
            campo_senha,
            ft.Container(
                content=ft.Text("Esqueceu a senha? Contate o administrador.", size=12, color=ft.colors.GREY_500),
                alignment=ft.alignment.center_right
            ),
            ft.Container(height=5),
            btn_entrar,
            ft.Text("v2.0.1", size=10, color=ft.colors.GREY_400)
        ], horizontal_alignment="center", spacing=20),
        padding=40,
        width=400,
        bgcolor=COLOR_WHITE,
        border_radius=24,
        shadow=ft.BoxShadow(
            blur_radius=30,
            color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
            offset=ft.Offset(0, 10)
        )
    )