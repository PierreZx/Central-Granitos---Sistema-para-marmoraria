# src/views/budget_view.py

import flet as ft
from src.views.layout_base import LayoutBase
from src.views.components.budget_calculator import BudgetCalculator
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
    SHADOW_MD, BORDER_RADIUS_LG, COLOR_BACKGROUND
)
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime

def BudgetView(page: ft.Page):
    grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
    container = ft.Container(expand=True)

    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def carregar():
        grid.controls.clear()
        lista = firebase_service.get_orcamentos_lista()

        # CARD PARA NOVO ORÇAMENTO
        grid.controls.append(
            ft.Container(
                col={"xs":12,"sm":6,"md":4,"lg":3},
                height=160,
                padding=20,
                bgcolor=COLOR_WHITE,
                border_radius=BORDER_RADIUS_LG,
                border=ft.border.all(2, COLOR_PRIMARY),
                content=ft.Column([
                    ft.Icon(ft.icons.ADD_CIRCLE_OUTLINE, size=40, color=COLOR_PRIMARY),
                    ft.Text("Novo Orçamento", weight="bold", color=COLOR_PRIMARY)
                ], alignment="center", horizontal_alignment="center"),
                on_click=lambda _: popup_novo()
            )
        )

        for o in lista:
            grid.controls.append(card_cliente(o))

        container.content = ft.Column([
            ft.Text("Central de Orçamentos", size=28, weight="bold"),
            ft.Text("Gerencie os projetos e orçamentos dos seus clientes", color="grey"),
            ft.Divider(height=20, color="transparent"),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    def card_cliente(o):
        status = o.get("status","Em aberto")
        cor = COLOR_WARNING if status=="Em aberto" else COLOR_SUCCESS
        total = float(o.get("total_geral", 0))

        return ft.Container(
            col={"xs":12,"sm":6,"md":4,"lg":3},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(o.get("cliente_nome","Cliente"), weight="bold", size=16, overflow="ellipsis"),
                        ft.Text(o.get("cliente_contato",""), size=12, color="grey"),
                    ], expand=True, spacing=2),
                    ft.Container(
                        bgcolor=cor,
                        padding=ft.padding.symmetric(4,10),
                        border_radius=8,
                        content=ft.Text(status, size=9, color=COLOR_WHITE, weight="bold")
                    )
                ], alignment="spaceBetween", vertical_alignment="start"),
                ft.Divider(height=10),
                ft.Text(f"R$ {total:,.2f}", size=20, weight="bold", color=COLOR_PRIMARY),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT_NOTE_ROUNDED, tooltip="Editar Itens", on_click=lambda _: abrir_orcamento(o)),
                    ft.IconButton(ft.icons.PICTURE_AS_PDF_ROUNDED, tooltip="Gerar PDF", on_click=lambda _: gerar_pdf_orcamento(o)),
                    ft.IconButton(ft.icons.DELETE_OUTLINE_ROUNDED, icon_color=COLOR_ERROR, on_click=lambda _: confirmar_delete(o))
                ], alignment="end", spacing=0)
            ])
        )

    def popup_novo():
        nome = ft.TextField(label="Nome do Cliente", border_radius=10)
        contato = ft.TextField(label="Contato (WhatsApp)", border_radius=10)
        endereco = ft.TextField(label="Endereço da Obra", border_radius=10)

        def salvar(e):
            if not nome.value: return
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
            content=ft.Column([nome, contato, endereco], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Criar Agora", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar)
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
            title=ft.Text("Excluir"),
            content=ft.Text(f"Deseja apagar o orçamento de {o['cliente_nome']}?"),
            actions=[
                ft.TextButton("Voltar", on_click=fechar_dialogo),
                ft.ElevatedButton("Sim, Excluir", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=deletar)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_orcamento(o):
        container.content = editor_orcamento(o)
        page.update()

    def editor_orcamento(o):
        def atualizar_total():
            o["total_geral"] = sum(float(i.get("preco_total", 0)) for i in o.get("itens", []))
            firebase_service.update_document("orcamentos", o["id"], o)

        def adicionar_item(e):
            def salvar_item(item):
                o["itens"].append(item)
                atualizar_total()
                abrir_orcamento(o)

            # Aqui chamaremos a calculadora reformulada
            container.content = BudgetCalculator(
                page,
                on_save_item=salvar_item,
                on_cancel=lambda _: abrir_orcamento(o)
            )
            page.update()

        def editar_item(item):
            def salvar_item_editado(novo_item):
                idx = o["itens"].index(item)
                o["itens"][idx] = novo_item
                atualizar_total()
                abrir_orcamento(o)

            # PASSANDO O 'item' PARA EDIÇÃO (Isso resolve o erro do Render)
            container.content = BudgetCalculator(
                page,
                item=item, 
                on_save_item=salvar_item_editado,
                on_cancel=lambda _: abrir_orcamento(o)
            )
            page.update()

        def excluir_item(item):
            o["itens"].remove(item)
            atualizar_total()
            abrir_orcamento(o)

        # LISTA DE ITENS REESTRUTURADA (FIM DOS ITENS ESTICADOS)
        lista_cards = []
        for item in o.get("itens", []):
            card_item = ft.Container(
                padding=15,
                bgcolor=COLOR_WHITE,
                border_radius=10,
                border=ft.border.all(1, "grey100"),
                content=ft.Row([
                    ft.Icon(ft.icons.ARCHITECTURE, color=COLOR_PRIMARY),
                    ft.Column([
                        ft.Text(item.get('material', 'Pedra'), weight="bold"),
                        ft.Text(f"{item.get('largura')}m x {item.get('profundidade')}m | {item.get('ambiente', 'Geral')}", size=12, color="grey"),
                    ], expand=True),
                    ft.Text(f"R$ {float(item.get('preco_total', 0)):,.2f}", weight="bold"),
                    ft.Row([
                        ft.IconButton(ft.icons.EDIT_OUTLINED, icon_size=18, on_click=lambda e, it=item: editar_item(it)),
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_size=18, icon_color=COLOR_ERROR, on_click=lambda e, it=item: excluir_item(it))
                    ], spacing=0)
                ])
            )
            lista_cards.append(card_item)

        total_atual = sum(float(i.get("preco_total", 0)) for i in o.get("itens", []))

        return ft.Column([
            ft.Container(
                padding=ft.padding.only(bottom=10),
                content=ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: carregar()),
                    ft.Column([
                        ft.Text(o["cliente_nome"], size=22, weight="bold"),
                        ft.Text("Itens do Orçamento", color="grey"),
                    ], spacing=0)
                ])
            ),
            ft.Column(lista_cards, spacing=8),
            ft.Divider(height=30),
            ft.Row([
                ft.Column([
                    ft.Text("Investimento Total", size=12, color="grey"),
                    ft.Text(f"R$ {total_atual:,.2f}", weight="bold", size=24, color=COLOR_PRIMARY),
                ], spacing=0),
                ft.ElevatedButton(
                    "Adicionar Peça", 
                    icon=ft.icons.ADD, 
                    bgcolor=COLOR_PRIMARY, 
                    color=COLOR_WHITE,
                    height=50,
                    on_click=adicionar_item
                )
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO)

    carregar()
    return LayoutBase(page, container, titulo="Orçamentos")