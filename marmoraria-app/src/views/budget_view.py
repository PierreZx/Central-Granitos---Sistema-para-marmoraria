# src/views/budget_view.py

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

    # ------------------ CARREGAR LISTA DE CLIENTES ------------------
    def carregar():
        grid.controls.clear()
        lista = firebase_service.get_orcamentos_lista()

        # CARD PARA CRIAR NOVO ORÇAMENTO
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
                grid.controls.append(card_cliente(o))

        container.content = ft.Column([
            ft.Text("Orçamentos", size=28, weight="bold"),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    # ------------------ CARD DE CLIENTE ------------------
    def card_cliente(o):
        status = o.get("status","Em aberto")
        cor = COLOR_WARNING if status=="Em aberto" else COLOR_SUCCESS

        total = sum(float(i.get("preco_total",0)) for i in o.get("itens",[]))

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
                ft.Text(f"Total: R$ {total:,.2f}", size=16, weight="bold", color=COLOR_PRIMARY),
                ft.Divider(),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT, on_click=lambda _: abrir_orcamento(o)),
                    ft.IconButton(ft.icons.PICTURE_AS_PDF, on_click=lambda _: gerar_pdf_orcamento(o)),
                    ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda _: confirmar_delete(o))
                ], alignment="end")
            ])
        )

    # ------------------ POPUP DE NOVO ORÇAMENTO ------------------
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

    # ------------------ CONFIRMAR DELETE ------------------
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

    # ------------------ EDITOR DO ORÇAMENTO ------------------
    def abrir_orcamento(o):
        container.content = editor_orcamento(o)
        page.update()

    def editor_orcamento(o):
        def atualizar_total():
            o["total_geral"] = sum(float(i["preco_total"]) for i in o.get("itens",[]))
            firebase_service.update_document("orcamentos", o["id"], o)

        # Função para adicionar item usando a calculadora
        def adicionar_item(*args):
            def salvar_item(item):
                o["itens"].append(item)
                atualizar_total()
                abrir_orcamento(o)

            container.content = BudgetCalculator(
                page,
                on_save_item=salvar_item,
                on_cancel=lambda _: abrir_orcamento(o)
            )
            page.update()

        # Função para editar item existente
        def editar_item(item):
            def salvar_item_editado(novo_item):
                idx = o["itens"].index(item)
                o["itens"][idx] = novo_item
                atualizar_total()
                abrir_orcamento(o)

            container.content = BudgetCalculator(
                page,
                item=item,
                on_save_item=salvar_item_editado,
                on_cancel=lambda _: abrir_orcamento(o)
            )
            page.update()

        # Função para excluir item
        def excluir_item(item):
            o["itens"].remove(item)
            atualizar_total()
            abrir_orcamento(o)

        # Agrupar itens por ambiente
        ambientes = {}
        for i in o.get("itens", []):
            ambiente = i.get("ambiente", "Sem ambiente")
            if ambiente not in ambientes:
                ambientes[ambiente] = []
            ambientes[ambiente].append(i)

        cards_ambientes = []
        for amb, itens in ambientes.items():
            lista_itens = ft.Column([
                ft.ListTile(
                    title=ft.Text(f"{item['material']}"),
                    subtitle=ft.Text(f"R$ {float(item['preco_total']):,.2f}"),
                    trailing=ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, it=item: editar_item(it)),
                        ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda e, it=item: excluir_item(it))
                    ])
                ) for item in itens
            ])
            card = ft.Container(
                padding=15,
                bgcolor=COLOR_WHITE,
                border_radius=BORDER_RADIUS_LG,
                shadow=SHADOW_MD,
                content=ft.Column([
                    ft.Text(amb, weight="bold", size=14),
                    lista_itens
                ])
            )
            cards_ambientes.append(card)

        total_atual = sum(float(i["preco_total"]) for i in o.get("itens", []))

        return ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: carregar()),
                    ft.Text(o["cliente_nome"], size=20, weight="bold")]),
            ft.Column(cards_ambientes, spacing=10),
            ft.Divider(),
            ft.Row([
                ft.Text(f"Total do Orçamento: R$ {total_atual:,.2f}", weight="bold", size=16, color=COLOR_PRIMARY),
                ft.ElevatedButton("Adicionar Pedra", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE,
                                  on_click=adicionar_item)
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO)

    carregar()
    return LayoutBase(page, container, titulo="Orçamentos")
