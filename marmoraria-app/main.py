import flet as ft
import os

def main(page: ft.Page):
    page.title = "Teste Marmoraria"
    page.bgcolor = "#722F37" 
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("SISTEMA CENTRAL GRANITOS", color="white", size=30, weight="bold"),
                ft.Text("Versão 0.25.2 instalada com sucesso!", color="white"),
                ft.ElevatedButton("Entrar no Sistema", on_click=lambda _: page.go("/login"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#722F37",
            padding=50,
            border_radius=20
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")