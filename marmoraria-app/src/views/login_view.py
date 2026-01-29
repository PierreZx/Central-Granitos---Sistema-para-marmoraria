import flet as ft
from src.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_WHITE,
    COLOR_BACKGROUND,
    AUTH_EMAIL,
    AUTH_PASSWORD,
    COLOR_TEXT,
)

# =========================================================
# ====================== LOGIN VIEW =======================
# =========================================================

def LoginView(page: ft.Page):

    # -----------------------------------------------------
    # ------------------ FEEDBACK UI ----------------------
    # -----------------------------------------------------

    def show_snack(msg: str, success: bool = True):
        snack = ft.SnackBar(
            content=ft.Text(
                    msg,
                    color="white",
                    weight="bold"
                ),
            bgcolor="green600" if success else "red600",
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=20,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # -----------------------------------------------------
    # ------------------ RESET BUTTON ---------------------
    # -----------------------------------------------------

    def reset_button():
        btn_entrar.disabled = False
        btn_entrar.content = ft.Text(
            "Entrar",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        page.update()

    # -----------------------------------------------------
    # ------------------ LOGIN ACTION ---------------------
    # -----------------------------------------------------

    def realizar_login(e):
        btn_entrar.disabled = True
        btn_entrar.content = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            color="white",
        )
        page.update()

        email = (campo_usuario.value or "").strip()
        senha = (campo_senha.value or "").strip()

        if not email or not senha:
            show_snack("Por favor, preencha todos os campos!", success=False)
            reset_button()
            return

        # Define papel do usuário
        role = "admin" if email == AUTH_EMAIL else "producao"
        setattr(page, "user_role", role)

        acesso_producao = (
            email == "acesso.producao@gmail.com"
            and senha == "MarmorariaC55"
        )
        acesso_admin = email == AUTH_EMAIL and senha == AUTH_PASSWORD

        if acesso_producao or acesso_admin:
            show_snack("Acesso autorizado. Bem-vindo!")

            if acesso_producao:
                page.go("/producao")
            else:
                page.go("/dashboard")
        else:
            show_snack("E-mail ou senha inválidos.", success=False)
            reset_button()

    # -----------------------------------------------------
    # ------------------ COMPONENTES ----------------------
    # -----------------------------------------------------

    logo_icon = ft.Container(
        content=ft.Image(src="icon.png", width=80, height=80),
        padding=10,
    )

    titulo = ft.Column(
        controls=[
            ft.Text(
                "CENTRAL GRANITOS",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=COLOR_PRIMARY,
            ),
            ft.Text(
                "Sistema de Gestão Interna",
                size=14,
                color="grey600",
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
    )

    campo_usuario = ft.TextField(
        label="E-mail",
        prefix_icon="email_outlined",   # ✅ Flet 0.23.2
        border_radius=12,
        filled=True,
        bgcolor="grey50",
        value=AUTH_EMAIL,
        on_submit=realizar_login,
        width=400,
    )

    campo_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon="lock_outline",     # ✅ Flet 0.23.2
        border_radius=12,
        filled=True,
        bgcolor="grey50",
        on_submit=realizar_login,
        width=400,
    )

    btn_entrar = ft.ElevatedButton(
        content=ft.Text(
            "Entrar",
            size=16,
            weight=ft.FontWeight.BOLD,
        ),
        height=55,
        width=400,
        style=ft.ButtonStyle(
            color=COLOR_WHITE,
            bgcolor=COLOR_PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=realizar_login,
    )

    # -----------------------------------------------------
    # ------------------ CONTAINER FINAL ------------------
    # -----------------------------------------------------

    return ft.Container(
        content=ft.Column(
            controls=[
                logo_icon,
                titulo,
                ft.Container(height=10),
                campo_usuario,
                campo_senha,
                ft.Container(
                    content=ft.Text(
                        "Esqueceu a senha? Contate o administrador.",
                        size=12,
                        color="grey500",
                    ),
                    alignment=ft.alignment.center_right,
                    width=400,
                ),
                btn_entrar,
                ft.Text("v2.5.0", size=10, color="grey400"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=40,
        width=420,
        bgcolor=COLOR_WHITE,
        border_radius=24,
        shadow=ft.BoxShadow(
            blur_radius=30,
            color="black12",
            offset=ft.Offset(0, 10),
        ),
    )
