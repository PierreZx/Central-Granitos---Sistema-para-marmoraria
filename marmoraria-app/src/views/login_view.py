import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE, AUTH_EMAIL, AUTH_PASSWORD
from src.services import firebase_service
from src.controllers.auth_controller import AuthController

def LoginView(page: ft.Page):
    """Tela de login responsiva (Compatível com Flet 0.22.1)"""

    radius = 16
    shadow = ft.BoxShadow(blur_radius=18, color="#00000014", offset=ft.Offset(0, 6))

    gradiente_fundo = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[ft.colors.BLUE_GREY_50, ft.colors.GREY_100, ft.colors.WHITE],
    )

    AUTHORIZED_EMAIL = AUTH_EMAIL
    AUTHORIZED_PASSWORD = AUTH_PASSWORD

    def show_snack(msg: str, success: bool = True):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=COLOR_WHITE),
            bgcolor=ft.colors.GREEN_400 if success else ft.colors.RED_400,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    def realizar_login(e):
            btn_entrar.disabled = True
            btn_entrar.content = ft.Row(
                [ft.ProgressRing(width=16, height=16, stroke_width=2, color=COLOR_WHITE), ft.Text("Entrando...", color=COLOR_WHITE)], 
                alignment=ft.MainAxisAlignment.CENTER
            )
            page.update()

            email = campo_usuario.value
            senha = campo_senha.value

            sucesso, mensagem = AuthController.autenticar(email, senha)

            if sucesso:
                show_snack(mensagem, success=True)
                page.go("/dashboard")
            else:
                btn_entrar.disabled = False
                btn_entrar.content = ft.Text("Entrar", size=16, weight=ft.FontWeight.W_600)
                
                container_form.offset = ft.Offset(-0.02, 0)
                page.update()
                import time
                time.sleep(0.06)
                container_form.offset = ft.Offset(0.02, 0)
                page.update()
                time.sleep(0.06)
                container_form.offset = ft.Offset(0, 0)
                page.update()
                
                show_snack(mensagem, success=False)

    def on_submit(e):
        realizar_login(e)

    logo = ft.Container(
        content=ft.Image(src="logo.png", width=140, height=140, fit=ft.ImageFit.CONTAIN),
        padding=ft.padding.only(bottom=8),
    )

    # CORREÇÃO: ft.icons (minúsculo)
    campo_usuario = ft.TextField(
        label="E-mail",
        hint_text="Digite seu e-mail cadastrado",
        height=56,
        text_size=15,
        border_radius=12,
        filled=True,
        fill_color=ft.colors.WHITE,
        focused_border_color=COLOR_PRIMARY,
        cursor_color=COLOR_PRIMARY,
        prefix_icon=ft.Icon(ft.icons.PERSON_OUTLINE, size=20, color=ft.colors.GREY_500),
        on_submit=on_submit,
    )

    campo_senha = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        height=56,
        text_size=15,
        border_radius=12,
        filled=True,
        fill_color=ft.colors.WHITE,
        focused_border_color=COLOR_PRIMARY,
        cursor_color=COLOR_PRIMARY,
        prefix_icon=ft.Icon(ft.icons.LOCK_OUTLINE, size=20, color=ft.colors.GREY_500),
        on_submit=on_submit,
    )

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight=ft.FontWeight.W_600),
        height=56,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_WHITE,
        on_click=realizar_login,
    )

    texto_esqueci_senha = ft.TextButton(text="Esqueceu sua senha?", on_click=lambda e: show_snack("Funcionalidade em breve", success=True))

    texto_rodape = ft.Column([
        ft.Divider(height=1, color=ft.colors.GREY_200),
        ft.Text("Central Granitos © 2025", size=12, color=ft.colors.GREY_500),
        ft.Text("Todos os direitos reservados", size=10, color=ft.colors.GREY_400),
    ], alignment=ft.MainAxisAlignment.CENTER)

    container_form = ft.Container(
        content=ft.Column([
            logo,
            ft.Text("Bem-vindo de volta", size=26, weight=ft.FontWeight.W_700, color=ft.colors.GREY_900),
            ft.Text("Faça login para continuar", size=14, color=ft.colors.GREY_600),
            ft.Divider(height=30, color=ft.colors.TRANSPARENT),
            campo_usuario,
            ft.Divider(height=12, color=ft.colors.TRANSPARENT),
            campo_senha,
            ft.Container(content=texto_esqueci_senha, alignment=ft.alignment.center_right),
            ft.Divider(height=18, color=ft.colors.TRANSPARENT),
            btn_entrar,
            ft.Divider(height=12, color=ft.colors.TRANSPARENT),
            texto_rodape,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
        bgcolor=ft.colors.WHITE,
        padding=36,
        border_radius=radius,
        shadow=shadow,
    )

    container_imagem = ft.Container(
        content=ft.Stack([
            ft.Image(src="marmores.jpg", fit=ft.ImageFit.COVER, opacity=0.95),
            ft.Container(
                gradient=ft.LinearGradient(begin=ft.alignment.center_left, end=ft.alignment.center_right, colors=["#00000099", ft.colors.TRANSPARENT])
            )
        ]),
        expand=True,
    )

    layout_desktop = ft.Row(
        controls=[
            ft.Container(content=container_imagem, expand=True),
            ft.Container(content=container_form, expand=True, alignment=ft.alignment.center, padding=40, bgcolor=gradiente_fundo),
        ],
        spacing=0,
        expand=True,
    )

    layout_mobile = ft.Column([
        ft.Container(height=220, content=ft.Image(src="marmores.jpg", fit=ft.ImageFit.COVER)),
        ft.Container(content=container_form, expand=True, padding=18, bgcolor=gradiente_fundo),
    ], expand=True)

    def ajustar_layout(e=None):
        if page.width < 760:
            page.controls.clear()
            page.controls.append(ft.Container(content=layout_mobile, expand=True))
        else:
            page.controls.clear()
            page.controls.append(ft.Container(content=layout_desktop, expand=True))

        largura_form = 420 if page.width >= 760 else max(300, page.width - 48)
        campo_usuario.width = largura_form
        campo_senha.width = largura_form
        btn_entrar.width = largura_form
        container_form.width = largura_form + 72 if page.width >= 760 else largura_form

        page.update()

    page.on_resize = ajustar_layout
    ajustar_layout()

    return ft.View(route="/", padding=0, controls=[ft.Container(content=layout_mobile if page.width < 760 else layout_desktop, expand=True)], bgcolor=gradiente_fundo)