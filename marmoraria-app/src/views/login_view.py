# src/views/login_view.py
import flet as ft
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT, COLOR_BACKGROUND
)
from src.services import firebase_service

def LoginView(page: ft.Page):
    # REMOVIDO: page.vertical_alignment daqui. 
    # Isso deve ser controlado pelo container principal para evitar crash.

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
            # Login Híbrido: Verifica SQLite local primeiro
            sucesso = firebase_service.verify_user_password(email, senha)

            if sucesso:
                # IMPORTANTE: Definir o user_role para o main.py permitir a entrada
                # Como você está usando admin padrão:
                page.session.set("user_role", "admin") 
                page.session.set("user_email", email)
                
                show_snack(f"Bem-vindo!")
                
                # Sincronização silenciosa
                if firebase_service.verificar_conexao():
                    firebase_service.sync_local_to_cloud()

                page.go("/dashboard")
            else:
                show_snack("E-mail ou senha incorretos.", False)
                reset_button()

        except Exception as ex:
            show_snack(f"Erro de acesso: {ex}", False)
            reset_button()

    def reset_button():
        btn_entrar.disabled = False
        btn_entrar.content = ft.Text("Entrar", size=16, weight="bold")
        page.update()

    # --- COMPONENTES ---
    
    logo_icon = ft.Container(
        content=ft.Icon(ft.icons.ARCHITECTURE_ROUNDED, size=80, color=COLOR_PRIMARY),
        margin=ft.margin.only(bottom=10)
    )

    titulo = ft.Column([
        ft.Text("CENTRAL", size=32, weight="black", color=COLOR_PRIMARY, spacing=-2),
        ft.Text("GRANITOS", size=18, weight="w500", color=COLOR_TEXT, letter_spacing=4),
    ], horizontal_alignment="center", spacing=0)

    campo_usuario = ft.TextField(
        label="E-mail",
        value="marmoraria.central@gmail.com", # Facilitador para teste no APK
        prefix_icon=ft.icons.PERSON_OUTLINE,
        border_radius=12,
        bgcolor=ft.colors.GREY_50,
        keyboard_type=ft.KeyboardType.EMAIL
    )

    campo_senha = ft.TextField(
        label="Senha",
        value="MarmorariaC55", # Facilitador para teste no APK
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        border_radius=12,
        bgcolor=ft.colors.GREY_50,
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

    # Layout centralizado usando um Container mestre que expande
    return ft.Container(
        content=ft.Column([
            logo_icon,
            titulo,
            ft.Container(height=10),
            campo_usuario,
            campo_senha,
            ft.Container(height=10),
            btn_entrar,
            ft.Text("v2.1.0 - APK Stable", size=10, color=ft.colors.GREY_400),
        ], 
        horizontal_alignment="center",
        alignment="center",
        tight=True,
        width=300
        ),
        alignment=ft.alignment.center, # Isso centraliza o card na tela do celular
        expand=True,
        bgcolor=COLOR_BACKGROUND
    )