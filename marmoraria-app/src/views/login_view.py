import flet as ft

def LoginView(page: ft.Page):
    # Cores fixas (Hardcoded) para garantir que nada venha NULL
    COLOR_PRIMARY = "#722F37" # Vinho
    COLOR_WHITE = "#FFFFFF"

    def realizar_login(e):
        # Lógica de login simples para teste de entrada
        if campo_usuario.value == "admin" and campo_senha.value == "123":
            page.go("/dashboard")
        else:
            snack = ft.SnackBar(ft.Text("Usuário ou senha incorretos"), bgcolor="red")
            page.overlay.append(snack)
            snack.open = True
            page.update()

    # Componentes com valores fixos
    logo = ft.Text("CENTRAL GRANITOS", size=30, weight="bold", color=COLOR_PRIMARY)
    
    campo_usuario = ft.TextField(
        label="E-mail", 
        width=300, 
        border_radius=10, 
        bgcolor=COLOR_WHITE
    )
    
    campo_senha = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        width=300, 
        border_radius=10, 
        bgcolor=COLOR_WHITE
    )

    btn_entrar = ft.ElevatedButton(
        "ENTRAR",
        color=COLOR_WHITE,
        bgcolor=COLOR_PRIMARY,
        width=300,
        height=50,
        on_click=realizar_login
    )

    return ft.Container(
        content=ft.Column([
            logo,
            ft.Container(height=20),
            campo_usuario,
            ft.Container(height=10),
            campo_senha,
            ft.Container(height=20),
            btn_entrar,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        expand=True
    )