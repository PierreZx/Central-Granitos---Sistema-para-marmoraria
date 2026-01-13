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
    main_container = ft.Container(expand=True)

    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def carregar_lista_orcamentos():
        """Carrega a grade principal de orçamentos do Firebase"""
        grid.controls.clear()
        lista = firebase_service.get_orcamentos_lista()

        # Botão para criar novo orçamento
        grid.controls.append(
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                padding=30,
                bgcolor=COLOR_WHITE,
                border_radius=BORDER_RADIUS_LG,
                border=ft.border.all(2, COLOR_PRIMARY),
                content=ft.Column([
                    ft.Icon(ft.icons.ADD_CIRCLE_OUTLINED, size=40, color=COLOR_PRIMARY),
                    ft.Text("Novo Orçamento", weight="bold", color=COLOR_PRIMARY)
                ], alignment="center", horizontal_alignment="center"),
                on_click=lambda _: exibir_popup_novo_cliente()
            )
        )

        # Adiciona os cards dos clientes existentes
        for orcamento in lista:
            grid.controls.append(criar_card_cliente(orcamento))

        main_container.content = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.LIST_ALT_ROUNDED, color=COLOR_PRIMARY),
                ft.Text("Gestão de Orçamentos", size=28, weight="bold"),
            ]),
            ft.Divider(height=10, color="transparent"),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    def criar_card_cliente(o):
        """Cria o card individual para cada orçamento na lista principal"""
        status = o.get("status", "Em aberto")
        cor_status = COLOR_WARNING if status == "Em aberto" else COLOR_SUCCESS
        
        # Garante que o valor total seja exibido corretamente como moeda
        valor_total = float(o.get("total_geral", 0))

        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            content=ft.Column([
                ft.Row([
                    ft.Text(o.get("cliente_nome", "Cliente"), weight="bold", size=18, overflow="ellipsis"),
                    ft.Container(
                        bgcolor=cor_status,
                        padding=ft.padding.symmetric(4, 10),
                        border_radius=10,
                        content=ft.Text(status.upper(), size=9, color=COLOR_WHITE, weight="bold")
                    )
                ], alignment="spaceBetween"),
                ft.Text(f"Investimento: R$ {valor_total:,.2f}", size=15, weight="w600", color=COLOR_PRIMARY),
                ft.Text(f"Data: {o.get('data','')[:10]}", size=11, color="grey"),
                ft.Divider(height=20),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT_NOTE_ROUNDED, tooltip="Editar Itens", on_click=lambda _: gerenciar_itens_orcamento(o)),
                    ft.IconButton(ft.icons.PICTURE_AS_PDF_ROUNDED, tooltip="Gerar PDF", on_click=lambda _: gerar_pdf_orcamento(o)),
                    ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, icon_color=COLOR_ERROR, tooltip="Excluir", on_click=lambda _: confirmar_exclusao(o))
                ], alignment="end")
            ])
        )

    def exibir_popup_novo_cliente():
        """Abre o diálogo para iniciar um novo orçamento de cliente"""
        nome_input = ft.TextField(label="Nome do Cliente", border_radius=10)
        contato_input = ft.TextField(label="Telefone / WhatsApp", border_radius=10)
        endereco_input = ft.TextField(label="Endereço da Obra", border_radius=10)

        def salvar_novo_cliente(e):
            if not nome_input.value:
                nome_input.error_text = "Campo obrigatório"
                page.update()
                return

            novo_orcamento = {
                "cliente_nome": nome_input.value,
                "cliente_contato": contato_input.value,
                "cliente_endereco": endereco_input.value,
                "status": "Em aberto",
                "itens": [],
                "total_geral": 0.0,
                "data": datetime.datetime.now().isoformat()
            }
            firebase_service.add_document("orcamentos", novo_orcamento)
            fechar_dialogo()
            carregar_lista_orcamentos()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Iniciar Novo Orçamento"),
            content=ft.Column([nome_input, contato_input, endereco_input], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Criar Orçamento", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_novo_cliente)
            ],
            actions_alignment="end"
        )
        page.dialog.open = True
        page.update()

    def confirmar_exclusao(o):
        def acao_deletar(e):
            firebase_service.delete_document("orcamentos", o["id"])
            fechar_dialogo()
            carregar_lista_orcamentos()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Deseja apagar o orçamento de {o.get('cliente_nome')}?"),
            actions=[
                ft.TextButton("Manter", on_click=fechar_dialogo),
                ft.ElevatedButton("Excluir", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=acao_deletar)
            ]
        )
        page.dialog.open = True
        page.update()

    def gerenciar_itens_orcamento(o):
        """Navega para a tela interna de edição dos itens (pedras) do orçamento"""
        main_container.content = view_detalhes_orcamento(o)
        page.update()

    def view_detalhes_orcamento(o):
        """Constrói a visualização detalhada com a lista de pedras do cliente"""
        
        def salvar_e_recalcular():
            # Soma os preços totais de cada peça para atualizar o cabeçalho do orçamento
            soma_total = sum(float(item.get("preco_total", 0)) for item in o.get("itens", []))
            o["total_geral"] = soma_total
            firebase_service.update_document("orcamentos", o["id"], o)

        def adicionar_nova_pedra(e=None):
            def callback_salvar(nova_peca):
                o["itens"].append(nova_peca)
                salvar_e_recalcular()
                gerenciar_itens_orcamento(o)

            main_container.content = BudgetCalculator(
                page,
                on_save_item=callback_salvar,
                on_cancel=lambda _: gerenciar_itens_orcamento(o)
            )
            page.update()

        def editar_pedra_existente(item):
            def callback_atualizar(peca_editada):
                indice = o["itens"].index(item)
                o["itens"][indice] = peca_editada
                salvar_e_recalcular()
                gerenciar_itens_orcamento(o)

            main_container.content = BudgetCalculator(
                page,
                item=item,
                on_save_item=callback_atualizar,
                on_cancel=lambda _: gerenciar_itens_orcamento(o)
            )
            page.update()

        def remover_pedra(item):
            o["itens"].remove(item)
            salvar_e_recalcular()
            gerenciar_itens_orcamento(o)

        # Geração da lista visual de pedras/itens
        lista_cards_pedras = []
        for item in o.get("itens", []):
            card_item = ft.Container(
                padding=15,
                bgcolor=COLOR_WHITE,
                border_radius=BORDER_RADIUS_LG,
                border=ft.border.all(1, "grey200"),
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"{item.get('material')} - {item.get('ambiente')}", weight="bold", size=16),
                        ft.Text(f"Medidas: {item.get('largura')}m x {item.get('profundidade')}m", size=13),
                        ft.Text(f"Subtotal: R$ {float(item.get('preco_total', 0)):,.2f}", color=COLOR_PRIMARY, weight="bold", size=15)
                    ], expand=True),
                    ft.Row([
                        ft.IconButton(ft.icons.EDIT_ROUNDED, tooltip="Ajustar Medidas", on_click=lambda e, it=item: editar_pedra_existente(it)),
                        ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=COLOR_ERROR, tooltip="Remover", on_click=lambda e, it=item: remover_pedra(it))
                    ])
                ])
            )
            lista_cards_pedras.append(card_item)

        total_orcamento = float(o.get("total_geral", 0))

        return ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: carregar_lista_orcamentos()),
                ft.Column([
                    ft.Text(o["cliente_nome"], size=22, weight="bold"),
                    ft.Text("Detalhamento de Peças e Medidas", size=12, color="grey"),
                ], spacing=0)
            ]),
            ft.Divider(height=20),
            ft.Column(lista_cards_pedras, spacing=12),
            ft.Divider(height=30),
            ft.Container(
                padding=20,
                bgcolor="#f8f9fa",
                border_radius=15,
                content=ft.Row([
                    ft.Column([
                        ft.Text("INVESTIMENTO TOTAL DO PROJETO", size=12, color="grey", weight="bold"),
                        ft.Text(f"R$ {total_orcamento:,.2f}", weight="bold", size=26, color=COLOR_PRIMARY),
                    ]),
                    ft.ElevatedButton(
                        "Adicionar Peça",
                        icon=ft.icons.ADD_ROUNDED,
                        bgcolor=COLOR_PRIMARY,
                        color=COLOR_WHITE,
                        height=50,
                        on_click=adicionar_nova_pedra
                    )
                ], alignment="spaceBetween")
            )
        ], scroll=ft.ScrollMode.AUTO)

    # Inicialização da View
    carregar_lista_orcamentos()
    return LayoutBase(page, main_container, titulo="Orçamentos")