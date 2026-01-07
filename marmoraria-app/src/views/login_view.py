import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, COLOR_BACKGROUND, AUTH_EMAIL, AUTH_PASSWORD
from src.services import firebase_service

def LoginView(page: ft.Page):
    """Tela de login com cores Vinho/Bronze"""

    def show_snack(msg: str, success: bool = True):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=COLOR_WHITE),
            bgcolor=ft.colors.GREEN_600 if success else ft.colors.RED_600,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    def realizar_login(e):
        email = campo_usuario.value
        senha = campo_senha.value

        # Acesso produção
        if email == "acesso.producao@gmail.com" and senha == "MarmorariaC55":
            page.session.set("user_role", "producao")
            show_snack("Bem-vindo à Área de Produção!", success=True)
            page.go("/producao")
            return

        # Acesso ADM
        is_local_admin = (email == AUTH_EMAIL and senha == AUTH_PASSWORD)
        is_db_user = firebase_service.verify_user_password(email, senha)

        if is_local_admin or is_db_user:
            page.session.set("user_role", "admin")
            show_snack("Login realizado com sucesso!", success=True)
            page.go("/dashboard")
        else:
            show_snack("E-mail ou senha incorretos", success=False)

    logo = ft.Container(
        content=ft.Column([
            ft.Image(src="logo.jpg", width=80, height=80, fit=ft.ImageFit.CONTAIN),
            ft.Text("CENTRAL", size=24, weight=ft.FontWeight.W_900, color=COLOR_PRIMARY),
            ft.Text("GRANITOS", size=14, weight=ft.FontWeight.W_600, color=COLOR_SECONDARY, style=ft.TextStyle(letter_spacing=2)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.only(bottom=20),
    )

    campo_usuario = ft.TextField(label="E-mail", height=50, border_radius=10, filled=True, focused_border_color=COLOR_PRIMARY)
    campo_senha = ft.TextField(label="Senha", password=True, height=50, border_radius=10, filled=True, focused_border_color=COLOR_PRIMARY, can_reveal_password=True)

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight=ft.FontWeight.W_600),
        height=50,
        bgcolor=COLOR_PRIMARY, # VINHO SÓLIDO
        color=COLOR_WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=realizar_login,
    )

    container_form = ft.Container(
        content=ft.Column([
            logo,
            ft.Text("Bem-vindo de volta", size=20, weight=ft.FontWeight.W_700, color=COLOR_PRIMARY),
            ft.Container(height=20),
            campo_usuario,
            ft.Container(height=10),
            campo_senha,
            ft.Container(height=20),
            btn_entrar,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=COLOR_WHITE,
        padding=40,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=20, color="#00000010"),
        width=400
    )

    return ft.View(route="/", padding=0, controls=[ft.Container(content=container_form, alignment=ft.alignment.center, expand=True, bgcolor=COLOR_BACKGROUND)])