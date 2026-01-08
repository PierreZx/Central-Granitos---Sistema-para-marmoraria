import flet as ft
import os

def main(page: ft.Page):
    page.title = "Teste Marmoraria"
    page.bgcolor = "#722F37" # Vinho
    # Usei o nome antigo dos alinhamentos caso a versão ainda seja antiga
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    page.add(
        ft.Container(
            content=ft.Column([
                # Removi o ícone CONSTRUCTION que deu erro
                ft.Text("SISTEMA CENTRAL GRANITOS", color="white", size=30, weight="bold"),
                ft.Text("Se você está vendo isso, a versão foi atualizada!", color="white"),
                ft.ElevatedButton("Tentar Abrir Login Real", on_click=lambda _: page.go("/login"))
            ], horizontal_alignment="center"),
            bgcolor="#722F37",
            padding=50,
            border_radius=20
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")