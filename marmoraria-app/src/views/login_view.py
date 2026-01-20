import flet as ft
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT, COLOR_BACKGROUND
)
from src.services import firebase_service

def LoginView(page: ft.Page):
    # Centralização do layout para mobile
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def show_snack(msg: str, success: bool = True):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=COLOR_WHITE, weight="w500"),
            bgcolor=ft.colors.GREEN_600 if success else ft.colors.RED_600,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def realizar_login(e):
        # 1. Feedback visual de carregamento (essencial no Android)
        btn_entrar.disabled = True
        btn_entrar.content = ft.ProgressRing(width=20, height=20, color=COLOR_WHITE, stroke_width=2)
        page.update()

        email = campo_usuario.value.strip().lower()
        senha = campo_senha.value.strip()

        if not email or not senha:
            show_snack("Preencha todos os campos!", False)
            reset_button()
            return

        try:
            # 2. LOGIN HÍBRIDO: 
            # Verifica primeiro no SQLite local (permite logar sem internet se já logou uma vez)
            sucesso = firebase_service.verify_user_password(email, senha)

            if sucesso:
                # Salva sessão básica no app
                page.session.set("user_email", email)
                show_snack(f"Bem-vindo, {email}!")
                
                # 3. Tenta sincronizar em segundo plano sem travar o login
                if firebase_service.verificar_conexao():
                    firebase_service.sync_local_to_cloud()

                page.go("/dashboard")
            else:
                show_snack("E-mail ou senha incorretos.", False)
                reset_button()

        except Exception as ex:
            show_snack(f"Erro ao acessar dados locais: {ex}", False)
            reset_button()

    def reset_button():
        btn_entrar.disabled = False
        btn_entrar.content = ft.Text("Entrar", size=16, weight="bold")
        page.update()

    # --- COMPONENTES VISUAIS ---
    
    logo_icon = ft.Container(
        content=ft.Icon(ft.icons.ARCHITECTURE_ROUNDED, size=80, color=COLOR_PRIMARY),
        margin=ft.margin.only(bottom=20)
    )

    titulo = ft.Column([
        ft.Text("CENTRAL", size=32, weight="black", color=COLOR_PRIMARY, spacing=-2),
        ft.Text("GRANITOS", size=18, weight="w500", color=COLOR_TEXT, letter_spacing=4),
    ], horizontal_alignment="center", spacing=0)

    campo_usuario = ft.TextField(
        label="E-mail",
        hint_text="seu@email.com",
        prefix_icon=ft.icons.PERSON_OUTLINE,
        border_radius=12,
        bgcolor=ft.colors.GREY_50,
        focused_border_color=COLOR_PRIMARY,
        keyboard_type=ft.KeyboardType.EMAIL
    )

    campo_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        border_radius=12,
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
        ),
        on_click=realizar_login,
        width=float("inf")
    )

    # Layout responsivo do Card de Login
    return ft.Container(
        content=ft.Column([
            logo_icon,
            titulo,
            ft.Container(height=20),
            campo_usuario,
            campo_senha,
            ft.Container(
                content=ft.Text("Acesso Offline Habilitado", size=11, color=ft.colors.GREY_400),
                alignment=ft.alignment.center
            ),
            ft.Container(height=10),
            btn_entrar,
            ft.Text("v2.1.0 - APK Stable", size=10, color=ft.colors.GREY_400),
        ], 
        horizontal_alignment="center",
        tight=True,
        width=320 # Largura ideal para a maioria dos celulares
        ),
        padding=40,
        bgcolor=COLOR_WHITE,
        border_radius=24,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.with_opacity(0.1, "black"))
    )