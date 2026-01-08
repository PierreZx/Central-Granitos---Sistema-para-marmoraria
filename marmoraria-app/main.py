import flet as ft
import os

def main(page: ft.Page):
    page.title = "Teste Marmoraria"
    page.bgcolor = "#722F37" # Vinho
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Se isso aqui não carregar, o problema é no servidor do Render/Flet
    # e não no seu código das telas.
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.CONSTRUCTION, size=50, color="white"),
                ft.Text("SISTEMA CENTRAL GRANITOS", color="white", size=30, weight="bold"),
                ft.Text("Se você está vendo isso, o código está funcionando!", color="white"),
                ft.ElevatedButton("Ir para Login Real", on_click=lambda _: page.go("/login"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#722F37",
            padding=50,
            border_radius=20
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")