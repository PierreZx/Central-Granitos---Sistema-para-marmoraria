# src/views/budget_view.py

import flet as ft
import os
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
        grid.controls.clear()
        # Busca a lista que agora vem do SQLite local ou Firebase
        lista = firebase_service.get_orcamentos_lista()

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

    def disparar_geracao_pdf(orcamento_data):
        # Feedback visual para o usuário no celular
        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.ProgressRing(size=20, stroke_width=2, color=COLOR_WHITE),
                ft.Text(" Gerando PDF profissional...")
            ]),
            bgcolor=COLOR_PRIMARY
        )
        page.snack_bar.open = True
        page.update()
        
        # 1. Gera o PDF em Base64 (sem salvar arquivo no disco do Android)
        pdf_b64 = gerar_pdf_orcamento(orcamento_data)
        
        if pdf_b64:
            # 2. Abre o PDF usando o Data URI. No Android/APK, isso dispara o visualizador padrão.
            url = f"data:application/pdf;base64,{pdf_b64}"
            page.launch_url(url)
            
            page.snack_bar.open = False # Fecha o aviso de "gerando"
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Erro ao gerar PDF. Verifique os dados."),
                bgcolor=COLOR_ERROR
            )
        page.update()

    def criar_card_cliente(o):
        status = o.get("status", "Em aberto")
        cor_status = COLOR_WARNING if status == "Em aberto" else COLOR_SUCCESS
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
                    ft.IconButton(
                        ft.icons.PICTURE_AS_PDF_ROUNDED, 
                        tooltip="Gerar PDF",
                        icon_color=ft.colors.RED_700,
                        on_click=lambda _: disparar_geracao_pdf(o) # Chamada corrigida
                    ),
                    ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, icon_color=COLOR_ERROR, on_click=lambda _: confirmar_exclusao(o))
                ], alignment="end")
            ])
        )

    def exibir_popup_novo_cliente():
        nome_input = ft.TextField(label="Nome do Cliente", border_radius=10)
        contato_input = ft.TextField(label="Telefone", border_radius=10)
        endereco_input = ft.TextField(label="Endereço", border_radius=10)

        def salvar_novo_cliente(e):
            if not nome_input.value: return
            novo = {
                "cliente_nome": nome_input.value,
                "cliente_contato": contato_input.value,
                "cliente_endereco": endereco_input.value,
                "status": "Em aberto",
                "itens": [],
                "total_geral": 0.0,
                "data": datetime.datetime.now().isoformat()
            }
            # Agora salva usando a lógica híbrida SQLite/Firebase
            firebase_service.add_document("orcamentos", novo)
            fechar_dialogo()
            carregar_lista_orcamentos()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Iniciar Novo Orçamento"),
            content=ft.Column([nome_input, contato_input, endereco_input], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Criar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_novo_cliente)
            ]
        )
        page.dialog.open = True
        page.update()

    def gerenciar_itens_orcamento(o):
        main_container.content = view_detalhes_orcamento(o)
        page.update()

    def view_detalhes_orcamento(o):

        def enviar_para_producao(e):
            o["status"] = "PENDENTE" 
            o["data_producao"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Atualiza no cache local e tenta subir para o Firebase
            if firebase_service.update_document("orcamentos", o["id"], o):
                page.snack_bar = ft.SnackBar(ft.Text("Orçamento enviado para a produção!"), bgcolor=COLOR_SUCCESS)
                page.snack_bar.open = True
                carregar_lista_orcamentos()
            page.update()

        def salvar_e_recalcular():
            soma_total = sum(float(item.get("preco_total", 0)) for item in o.get("itens", []))
            o["total_geral"] = soma_total
            firebase_service.update_document("orcamentos", o["id"], o)

        def adicionar_nova_pedra(e=None):
            def callback_salvar(nova_peca):
                o["itens"].append(nova_peca)
                salvar_e_recalcular()
                gerenciar_itens_orcamento(o)

            main_container.content = BudgetCalculator(
                page=page,
                on_save_item=callback_salvar,
                on_cancel=lambda: gerenciar_itens_orcamento(o)
            )
            page.update()

        def editar_pedra_existente(item):
            def callback_atualizar(peca_editada):
                indice = o["itens"].index(item)
                o["itens"][indice] = peca_editada
                salvar_e_recalcular()
                gerenciar_itens_orcamento(o)

            main_container.content = BudgetCalculator(
                page=page,
                item=item,
                on_save_item=callback_atualizar,
                on_cancel=lambda: gerenciar_itens_orcamento(o)
            )
            page.update()

        def remover_pedra(item):
            o["itens"].remove(item)
            salvar_e_recalcular()
            gerenciar_itens_orcamento(o)

        cards = []
        for i in o.get("itens", []):
            pecas_info = i.get('pecas', {})
            # Pega a primeira peça disponível para mostrar no resumo
            p1 = pecas_info.get('p1', {}) or next(iter(pecas_info.values()), {}) if pecas_info else {}
            
            cards.append(
                ft.Container(
                    padding=15, bgcolor=COLOR_WHITE, border_radius=BORDER_RADIUS_LG,
                    border=ft.border.all(1, "grey200"),
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"{i.get('material')} - {i.get('ambiente')}", weight="bold"),
                            ft.Text(f"Qtd: {i.get('quantidade', 1)} | Medida: {p1.get('l','0')}m x {p1.get('p','0')}m"),
                            ft.Text(f"R$ {float(i.get('preco_total', 0)):,.2f}", color=COLOR_PRIMARY, weight="bold")
                        ], expand=True),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, on_click=lambda e, it=i: editar_pedra_existente(it)),
                            ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda e, it=i: remover_pedra(it))
                        ])
                    ])
                )
            )

        return ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: carregar_lista_orcamentos()),
                ft.Text(o["cliente_nome"], size=22, weight="bold")
            ]),
            ft.Column(cards, spacing=10),
            ft.Divider(),
            ft.Row([
                ft.Text(f"Total: R$ {float(o.get('total_geral', 0)):,.2f}", weight="bold", size=26, color=COLOR_PRIMARY),
                ft.Row([
                    ft.ElevatedButton(
                        "Enviar Produção", 
                        icon=ft.icons.SEND_ROUNDED,
                        bgcolor=ft.colors.ORANGE_800, 
                        color=COLOR_WHITE, 
                        on_click=enviar_para_producao
                    ),
                    ft.ElevatedButton("Adicionar Peça", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=adicionar_nova_pedra)
                ], spacing=10)
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO)

    def confirmar_exclusao(o):
        def acao(e):
            firebase_service.delete_document("orcamentos", o["id"])
            fechar_dialogo()
            carregar_lista_orcamentos()
        page.dialog = ft.AlertDialog(title=ft.Text("Excluir?"), actions=[ft.TextButton("Sim", on_click=acao), ft.TextButton("Não", on_click=fechar_dialogo)])
        page.dialog.open = True
        page.update()

    carregar_lista_orcamentos()
    return LayoutBase(page, main_container, titulo="Orçamentos")