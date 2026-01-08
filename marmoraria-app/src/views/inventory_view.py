import flet as ft
from src.views.layout_base import LayoutBase
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
from src.services import firebase_service

def InventoryView(page: ft.Page):
    grid_produtos = ft.ResponsiveRow(spacing=20, run_spacing=20)

    def confirmar_exclusao(id):
        def deletar(e):
            firebase_service.delete_document("estoque", id)
            page.dialog.open = False
            carregar_dados()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Excluir Item?"),
            content=ft.Text("Esta ação não pode ser desfeita."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.TextButton("Excluir", on_click=deletar, color=COLOR_ERROR)
            ]
        )
        page.dialog.open = True
        page.update()

    def carregar_dados():
        grid_produtos.controls.clear()
        lista = firebase_service.get_collection("estoque")
        for item in lista:
            grid_produtos.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    padding=15, bgcolor=COLOR_WHITE, border_radius=10, shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Text(item.get('nome', 'Sem nome'), weight="bold"),
                        ft.Text(f"Qtd: {item.get('quantidade')} | {item.get('metros')} m²"),
                        ft.Row([
                            ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda e, id=item['id']: confirmar_exclusao(id))
                        ], alignment="end")
                    ])
                )
            )
        page.update()

    conteudo = ft.Column([
        ft.Row([ft.Text("Estoque", size=28, weight="bold"), ft.ElevatedButton("Novo", icon=ft.icons.ADD, on_click=lambda _: None)]),
        grid_produtos
    ], scroll=ft.ScrollMode.AUTO)

    carregar_dados()
    return LayoutBase(page, conteudo, "Estoque")