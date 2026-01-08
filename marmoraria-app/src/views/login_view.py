import flet as ft

def LoginView(page: ft.Page):
    # Cores fixas para evitar erros de importação
    VINHO = "#722F37"
    BRANCO = "#FFFFFF"

    def realizar_login(e):
        if campo_usuario.value == "admin" and campo_senha.value == "123":
            page.push_route("/dashboard")
        else:
            snack = ft.SnackBar(ft.Text("Login Inválido"), bgcolor="red")
            page.overlay.append(snack)
            snack.open = True
            page.update()

    logo = ft.Text("CENTRAL GRANITOS", size=32, weight="bold", color=VINHO)
    
    campo_usuario = ft.TextField(label="Usuário", width=300, border_radius=10)
    campo_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, border_radius=10)
    
    btn_entrar = ft.ElevatedButton(
        "ENTRAR", 
        color=BRANCO, 
        bgcolor=VINHO, 
        width=300, 
        height=50,
        on_click=realizar_login
    )

    return ft.Container(
        content=ft.Column([
            logo,
            ft.Container(height=20),
            campo_usuario,
            campo_senha,
            ft.Container(height=10),
            btn_entrar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center, # <--- CORRIGIDO AQUI (tudo minúsculo)
        expand=True,
        bgcolor="#F5F5F5"
    )