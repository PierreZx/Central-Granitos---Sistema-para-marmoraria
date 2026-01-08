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
                ft.Text("Conectado ao Python 3.13 e Flet 0.25.2!", color="white"),
                ft.ElevatedButton("Abrir Login", on_click=lambda _: page.go("/login"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#722F37",
            padding=50,
            border_radius=20
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    # Na versão 0.25.2, usamos apenas o target e as portas
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=port, 
        host="0.0.0.0"
    )