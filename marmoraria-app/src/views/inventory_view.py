import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY,
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING,
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service


def InventoryView(page: ft.Page):

    grid_produtos = ft.ResponsiveRow(spacing=20, run_spacing=20)

    # Campos do formulário
    txt_nome = ft.TextField(label="Nome da Pedra", filled=True, border_radius=BORDER_RADIUS_MD)
    txt_preco = ft.TextField(
        label="Preço por m²",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD
    )
    txt_metros = ft.TextField(
        label="Medida disponível",
        suffix_text="m²",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD,
        expand=True
    )
    txt_qtd = ft.TextField(
        label="Quantidade",
        suffix_text="un",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD,
        expand=True
    )

    # ------------------------
    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    # ------------------------
    def carregar_dados():
        grid_produtos.controls.clear()
        lista = firebase_service.get_collection("estoque")

        if not lista:
            grid_produtos.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum item no estoque."),
                    padding=50,
                    alignment=ft.alignment.center,
                    col=12
                )
            )
        else:
            for item in lista:
                grid_produtos.controls.append(
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 4, "xl": 3},
                        padding=20,
                        bgcolor=COLOR_WHITE,
                        border_radius=BORDER_RADIUS_MD,
                        shadow=SHADOW_MD,
                        content=ft.Column([
                            ft.Text(item.get("nome"), weight="bold", size=16),
                            ft.Text(f"R$ {item.get('preco_m2', 0):.2f} / m²", color=COLOR_PRIMARY),
                            ft.Text(f"{item.get('metros', 0)} m² disponíveis"),
                            ft.Text(f"{item.get('quantidade', 0)} unidades"),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    on_click=lambda e, i=item: abrir_popup_editar(i)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=COLOR_ERROR,
                                    on_click=lambda e, i=item: confirmar_exclusao(i["id"], i["nome"])
                                )
                            ], alignment="end")
                        ])
                    )
                )
        page.update()

    # ------------------------
    def salvar_produto(e):
        try:
            dados = {
                "nome": txt_nome.value,
                "preco_m2": float(txt_preco.value.replace(",", ".")),
                "metros": float(txt_metros.value.replace(",", ".")),
                "quantidade": int(txt_qtd.value or 0)
            }
            if firebase_service.add_document("estoque", dados):
                fechar_dialogo()
                carregar_dados()
        except ValueError:
            print("Erro nos valores numéricos")

    # ------------------------
    def abrir_popup_novo(e):
        txt_nome.value = ""
        txt_preco.value = ""
        txt_metros.value = ""
        txt_qtd.value = ""

        page.dialog = ft.AlertDialog(
            title=ft.Text("Nova Pedra"),
            content=ft.Column([
                txt_nome,
                txt_preco,
                ft.Row([txt_metros, txt_qtd], spacing=10)
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", on_click=salvar_produto)
            ]
        )
        page.dialog.open = True
        page.update()

    # ------------------------
    def abrir_popup_editar(item):
        txt_nome.value = item.get("nome")
        txt_preco.value = str(item.get("preco_m2", 0))
        txt_metros.value = str(item.get("metros", 0))
        txt_qtd.value = str(item.get("quantidade", 0))

        def salvar_edicao(e):
            try:
                dados = {
                    "nome": txt_nome.value,
                    "preco_m2": float(txt_preco.value.replace(",", ".")),
                    "metros": float(txt_metros.value.replace(",", ".")),
                    "quantidade": int(txt_qtd.value)
                }
                if firebase_service.update_document("estoque", item["id"], dados):
                    fechar_dialogo()
                    carregar_dados()
            except ValueError:
                print("Erro ao editar")

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Editar {item.get('nome')}"),
            content=ft.Column([
                txt_nome,
                txt_preco,
                ft.Row([txt_metros, txt_qtd], spacing=10)
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Atualizar", on_click=salvar_edicao)
            ]
        )
        page.dialog.open = True
        page.update()

    # ------------------------
    def confirmar_exclusao(id_item, nome):
        def deletar(e):
            firebase_service.delete_document("estoque", id_item)
            fechar_dialogo()
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Excluir"),
            content=ft.Text(f"Deseja excluir {nome}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.TextButton("Excluir", on_click=deletar)
            ]
        )
        page.dialog.open = True
        page.update()

    # ------------------------
    header = ft.Row([
        ft.Text("Estoque", size=28, weight="bold"),
        ft.ElevatedButton(
            "Adicionar Pedra",
            icon=ft.icons.ADD,
            on_click=abrir_popup_novo
        )
    ], alignment="spaceBetween")

    carregar_dados()

    return LayoutBase(
        page,
        ft.Column([header, ft.Divider(), grid_produtos], expand=True, scroll=ft.ScrollMode.AUTO),
        titulo="Estoque"
    )
