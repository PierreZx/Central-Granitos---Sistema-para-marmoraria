import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND,
    COLOR_PRIMARY,
    COLOR_WHITE,
    COLOR_TEXT,
    COLOR_ERROR,
)
from src.services import firebase_service


def InventoryView(page: ft.Page):

    # ================= GRID =================
    grid_produtos = ft.ResponsiveRow(
        spacing=20,
        run_spacing=20
    )

    # ================= CAMPOS =================
    txt_nome = ft.TextField(label="Nome da Pedra", filled=True, border_radius=12)

    txt_preco = ft.TextField(
        label="Preço por m²",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=12
    )

    txt_metros = ft.TextField(
        label="Medida disponível",
        suffix_text=" m²",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=12,
        expand=True
    )

    txt_qtd = ft.TextField(
        label="Quantidade",
        suffix_text=" un",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=12,
        expand=True
    )

    # ================= FUNÇÕES =================
    def carregar_dados():
        grid_produtos.controls.clear()

        lista = firebase_service.get_collection("estoque")

        if not lista:
            grid_produtos.controls.append(
                ft.Container(
                    col=12,
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Text("Nenhum item no estoque.", size=16),
                )
            )
        else:
            for produto in lista:
                grid_produtos.controls.append(
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 4, "xl": 3},
                        padding=20,
                        bgcolor=COLOR_WHITE,
                        border_radius=14,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color="black12",
                            offset=ft.Offset(0, 6),
                        ),
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    produto.get("nome", ""),
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"R$ {float(produto.get('preco_m2', 0)):,.2f} / m²",
                                    color=COLOR_PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(f"{produto.get('metros', 0)} m² disponíveis"),
                                ft.Text(f"{produto.get('quantidade', 0)} unidades"),
                                ft.Divider(height=10, color="transparent"),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon="edit",
                                            icon_color=COLOR_PRIMARY,
                                            tooltip="Editar",
                                            on_click=lambda e, p=produto: preparar_edicao(p),
                                        ),
                                        ft.IconButton(
                                            icon="delete_outline",
                                            icon_color=COLOR_ERROR,
                                            tooltip="Excluir",
                                            on_click=lambda e, p=produto: confirmar_exclusao(
                                                p["id"], p.get("nome", "")
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            spacing=6,
                        ),
                    )
                )

        page.update()

    # ================= EDITAR =================
    def preparar_edicao(item):
        txt_nome.value = item.get("nome", "")
        txt_preco.value = str(item.get("preco_m2", ""))
        txt_metros.value = str(item.get("metros", ""))
        txt_qtd.value = str(item.get("quantidade", ""))

        def salvar(e):
            dados = {
                "nome": txt_nome.value,
                "preco_m2": float(txt_preco.value.replace(",", ".") or 0),
                "metros": float(txt_metros.value.replace(",", ".") or 0),
                "quantidade": int(txt_qtd.value or 0),
            }
            firebase_service.update_document("estoque", item["id"], dados)
            page.close(dlg)
            carregar_dados()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Editar {item.get('nome', '')}"),
            content=ft.Column(
                controls=[
                    txt_nome,
                    txt_preco,
                    ft.Row([txt_metros, txt_qtd], spacing=10),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                ft.ElevatedButton(
                    "Atualizar",
                    bgcolor=COLOR_PRIMARY,
                    color=COLOR_WHITE,
                    on_click=salvar,
                ),
            ],
        )

        page.open(dlg)

    # ================= EXCLUIR =================
    def confirmar_exclusao(id_item, nome):
        def deletar(e):
            firebase_service.delete_document("estoque", id_item)
            page.close(dlg)
            carregar_dados()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Remover {nome} do estoque?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                ft.TextButton(
                    "Excluir",
                    style=ft.ButtonStyle(color=COLOR_ERROR),
                    on_click=deletar,
                ),
            ],
        )

        page.open(dlg)

    # ================= NOVO =================
    def preparar_novo(e):
        txt_nome.value = ""
        txt_preco.value = ""
        txt_metros.value = ""
        txt_qtd.value = ""

        def salvar(e):
            dados = {
                "nome": txt_nome.value,
                "preco_m2": float(txt_preco.value.replace(",", ".") or 0),
                "metros": float(txt_metros.value.replace(",", ".") or 0),
                "quantidade": int(txt_qtd.value or 0),
            }
            firebase_service.add_document("estoque", dados)
            page.close(dlg)
            carregar_dados()

        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar Nova Pedra"),
            content=ft.Column(
                controls=[
                    txt_nome,
                    txt_preco,
                    ft.Row([txt_metros, txt_qtd], spacing=10),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                ft.ElevatedButton(
                    "Salvar",
                    bgcolor=COLOR_PRIMARY,
                    color=COLOR_WHITE,
                    on_click=salvar,
                ),
            ],
        )

        page.open(dlg)

    # ================= HEADER =================
    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text(
                        "Gestão de Estoque",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT
                    ),
                    ft.Text(
                        "Controle de chapas e medidas",
                        color="grey600"
                    ),
                ]
            ),
            ft.ElevatedButton(
                "Adicionar Pedra",
                icon="add",
                height=50,
                bgcolor=COLOR_PRIMARY,
                color=COLOR_WHITE,
                on_click=preparar_novo,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    carregar_dados()

    return LayoutBase(
        page,
        ft.Column(
            controls=[
                header,
                ft.Divider(height=30, color="transparent"),
                grid_produtos,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        titulo="Estoque",
    )
