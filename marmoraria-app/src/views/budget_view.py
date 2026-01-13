import flet as ft
from src.views.layout_base import LayoutBase
from src.views.components.budget_calculator import BudgetCalculator
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
    SHADOW_MD, BORDER_RADIUS_LG
)
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime

def BudgetView(page: ft.Page):
    grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
    container = ft.Container(expand=True)

    # ------------------ HELPERS ------------------
    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def carregar():
        grid.controls.clear()
        lista = firebase_service.get_orcamentos_lista()

        # CARD NOVO
        grid.controls.append(
            ft.Container(
                col={"xs":12,"sm":6,"md":4,"lg":3},
                padding=30,
                bgcolor=COLOR_WHITE,
                border_radius=BORDER_RADIUS_LG,
                border=ft.border.all(2, COLOR_PRIMARY),
                content=ft.Column([
                    ft.Icon(ft.icons.ADD_CIRCLE, size=40, color=COLOR_PRIMARY),
                    ft.Text("Novo Orçamento", weight="bold", color=COLOR_PRIMARY)
                ], alignment="center", horizontal_alignment="center"),
                on_click=lambda _: popup_novo()
            )
        )

        if not lista:
            grid.controls.append(
                ft.Container(
                    col=12,
                    padding=40,
                    content=ft.Text("Nenhum orçamento criado ainda.", color="grey"),
                    alignment=ft.alignment.center
                )
            )
        else:
            for o in lista:
                grid.controls.append(card_orcamento(o))

        container.content = ft.Column([
            ft.Text("Orçamentos", size=28, weight="bold"),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    # ------------------ CARD ------------------
    def card_orcamento(o):
        status = o.get("status","Em aberto")
        cor = COLOR_WARNING if status=="Em aberto" else COLOR_SUCCESS

        return ft.Container(
            col={"xs":12,"sm":6,"md":4,"lg":3},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            content=ft.Column([
                ft.Row([
                    ft.Text(o.get("cliente_nome","Cliente"), weight="bold", size=16),
                    ft.Container(
                        bgcolor=cor,
                        padding=ft.padding.symmetric(6,12),
                        border_radius=12,
                        content=ft.Text(status, size=10, color=COLOR_WHITE)
                    )
                ], alignment="spaceBetween"),
                ft.Text(f"R$ {float(o.get('total_geral',0)):,.2f}", size=18, weight="bold", color=COLOR_PRIMARY),
                ft.Divider(),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT, on_click=lambda _: abrir_orcamento(o)),
                    ft.IconButton(ft.icons.PICTURE_AS_PDF, on_click=lambda _: gerar_pdf_orcamento(o)),
                    ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda _: confirmar_delete(o))
                ], alignment="end")
            ])
        )

    # ------------------ POPUPS ------------------
    def popup_novo():
        nome = ft.TextField(label="Nome do Cliente")
        contato = ft.TextField(label="Contato")
        endereco = ft.TextField(label="Endereço (opcional)")

        def salvar(e):
            dados = {
                "cliente_nome": nome.value,
                "cliente_contato": contato.value,
                "cliente_endereco": endereco.value,
                "status": "Em aberto",
                "itens": [],
                "total_geral": 0,
                "data": datetime.datetime.now().isoformat()
            }
            firebase_service.add_document("orcamentos", dados)
            fechar_dialogo()
            carregar()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Novo Orçamento"),
            content=ft.Column([nome, contato, endereco], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Criar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar)
            ]
        )
        page.dialog.open = True
        page.update()

    def confirmar_delete(o):
        def deletar(e):
            firebase_service.delete_document("orcamentos", o["id"])
            fechar_dialogo()
            carregar()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Excluir orçamento"),
            content=ft.Text("Deseja realmente excluir este orçamento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.TextButton("Excluir", on_click=deletar, style=ft.ButtonStyle(color=COLOR_ERROR))
            ]
        )
        page.dialog.open = True
        page.update()

    # ------------------ ORÇAMENTO ABERTO ------------------
    def abrir_orcamento(o):
        container.content = editor_orcamento(o)
        page.update()

    def editor_orcamento(o):
        def adicionar_item():
            def salvar_item(item):
                o["itens"].append(item)
                o["total_geral"] = sum(float(i["preco_total"]) for i in o["itens"])
                firebase_service.update_document("orcamentos", o["id"], o)
                abrir_orcamento(o)

            container.content = BudgetCalculator(
                page,
                on_save_item=salvar_item,
                on_cancel=lambda _: abrir_orcamento(o)
            )
            page.update()

        lista_itens = ft.Column([
            ft.ListTile(
                title=ft.Text(f"{i['ambiente']} - {i['material']}"),
                subtitle=ft.Text(f"R$ {float(i['preco_total']):,.2f}")
            ) for i in o.get("itens",[])
        ])

        return ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: carregar()),
                ft.Text(o["cliente_nome"], size=20, weight="bold")
            ]),
            lista_itens,
            ft.ElevatedButton(
                "Adicionar Pedra",
                icon=ft.icons.ADD,
                bgcolor=COLOR_PRIMARY,
                color=COLOR_WHITE,
                on_click=lambda _: adicionar_item()
            )
        ], scroll=ft.ScrollMode.AUTO)

    carregar()
    return LayoutBase(page, container, titulo="Orçamentos")
