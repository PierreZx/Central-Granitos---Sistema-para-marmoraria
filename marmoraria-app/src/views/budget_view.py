import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, SHADOW_MD
)
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime

def BudgetView(page: ft.Page):
    
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True)

    # --- FUNÇÃO AUXILIAR DE CONFIRMAÇÃO ---
    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        def acao_sim(e):
            ao_confirmar()
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(dlg, "open", False) or page.update()),
                ft.TextButton("Confirmar", style=ft.ButtonStyle(color=ft.colors.RED), on_click=acao_sim),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- LISTA PRINCIPAL (GRID) ---
    def render_lista_principal():
        # Busca a lista de orçamentos do Firebase
        lista_dados = firebase_service.get_collection("orcamentos")
        
        grid = ft.GridView(
            expand=True, 
            runs_count=3, 
            max_extent=350, 
            child_aspect_ratio=0.75, 
            spacing=20, 
            run_spacing=20
        )

        if not lista_dados:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.REQUEST_QUOTE, size=60, color=ft.colors.GREY_300), 
                        ft.Text("Sem orçamentos cadastrados.", color=ft.colors.GREY_400)
                    ], alignment=ft.MainAxisAlignment.CENTER), 
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            for orc in lista_dados:
                total = orc.get('total_geral', 0)
                status = orc.get('status', 'Pendente')
                
                # Cores de Status
                cor_st = COLOR_PRIMARY
                if status == 'Produção': cor_st = ft.colors.BLUE
                elif status == 'Finalizado': cor_st = COLOR_SUCCESS
                elif status == 'Cancelado': cor_st = COLOR_ERROR

                card = ft.Container(
                    bgcolor=COLOR_WHITE, 
                    border_radius=15, 
                    padding=20, 
                    shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(status, size=10, color="white", weight="bold"), 
                                bgcolor=cor_st, padding=5, border_radius=5
                            ),
                            ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=COLOR_ERROR, icon_size=18, on_click=lambda e, o=orc: mostrar_confirmacao("Excluir?", "Deseja apagar este orçamento?", lambda: excluir_orcamento(o)))
                        ], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', 'Sem Nome'), weight="bold", size=18, max_lines=1, overflow="ellipsis"),
                        ft.Text(f"Contato: {orc.get('cliente_contato', '-')}", size=12, color="grey"),
                        ft.Text(f"Endereço: {orc.get('cliente_endereco', '-')}", size=11, color="grey", max_lines=1),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("TOTAL:", weight="bold", size=11), 
                            ft.Text(f"R$ {total:,.2f}", weight="bold", size=18, color=COLOR_PRIMARY)
                        ], alignment="spaceBetween"),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Abrir Orçamento", 
                            bgcolor=COLOR_SECONDARY, 
                            color="white", 
                            width=float("inf"), 
                            on_click=lambda e, o=orc: carregar_editor(o)
                        )
                    ])
                )
                grid.controls.append(card)

        # --- POPUP NOVO CLIENTE ---
        txt_nome = ft.TextField(label="Nome do Cliente")
        txt_cont = ft.TextField(label="WhatsApp/Contato")
        txt_end = ft.TextField(label="Endereço da Obra")
        
        def criar_novo_orcamento_click(e):
            if not txt_nome.value: return
            novo = {
                "cliente_nome": txt_nome.value, 
                "cliente_contato": txt_cont.value, 
                "cliente_endereco": txt_end.value, 
                "itens": [], 
                "total_geral": 0.0, 
                "status": "Pendente",
                "data": datetime.datetime.now().isoformat()
            }
            # Adiciona ao Firebase
            sucesso = firebase_service.add_document("orcamentos", novo)
            if sucesso:
                page.dialog.open = False
                # Recarrega a lista para pegar o ID gerado ou busca o mais recente
                render_lista_principal()
                page.update()

        dialog_novo = ft.AlertDialog(
            title=ft.Text("Dados do Novo Cliente"),
            content=ft.Column([txt_nome, txt_cont, txt_end], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.ElevatedButton("Criar e Editar", bgcolor=COLOR_PRIMARY, color="white", on_click=criar_novo_orcamento_click)
            ]
        )

        def abrir_popup_novo(e):
            page.dialog = dialog_novo
            dialog_novo.open = True
            page.update()

        conteudo_principal.content = ft.Container(
            padding=30, 
            expand=True, 
            content=ft.Column([
                ft.Row([
                    ft.Text("Orçamentos", size=28, weight="bold", color=COLOR_PRIMARY), 
                    ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, text="Novo", on_click=abrir_popup_novo)
                ], alignment="spaceBetween"),
                ft.Divider(), 
                grid
            ])
        )
        page.update()

    def excluir_orcamento(o):
        firebase_service.delete_document("orcamentos", o['id'])
        render_lista_principal()

    # --- EDITOR DE ORÇAMENTO ---
    def carregar_editor(orcamento):
        estado['orcamento_atual'] = orcamento
        estado['id_atual'] = orcamento.get('id')
        if 'itens' not in estado['orcamento_atual']: 
            estado['orcamento_atual']['itens'] = []
        render_tela_editor()

    def render_tela_editor():
        orc = estado['orcamento_atual']
        
        # Campos de edição rápida
        txt_edit_nome = ft.TextField(label="Cliente", value=orc.get('cliente_nome'), expand=True)
        txt_edit_cont = ft.TextField(label="Contato", value=orc.get('cliente_contato'), expand=True)
        txt_edit_end = ft.TextField(label="Endereço", value=orc.get('cliente_endereco'), expand=True)

        def salvar_cabecalho(e):
            orc['cliente_nome'] = txt_edit_nome.value
            orc['cliente_contato'] = txt_edit_cont.value
            orc['cliente_endereco'] = txt_edit_end.value
            firebase_service.update_document("orcamentos", estado['id_atual'], orc)
            page.snack_bar = ft.SnackBar(ft.Text("Dados atualizados!"), bgcolor=COLOR_SUCCESS)
            page.snack_bar.open = True
            page.update()

        lista_itens_ui = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)
        total_calc = sum(float(i.get('preco_total', 0)) for i in orc['itens'])
        orc['total_geral'] = total_calc

        def remover_peca(idx):
            orc['itens'].pop(idx)
            firebase_service.update_document("orcamentos", estado['id_atual'], orc)
            render_tela_editor()

        for idx, item in enumerate(orc['itens']):
            lista_itens_ui.controls.append(
                ft.Container(
                    bgcolor=ft.colors.GREY_50, padding=15, border_radius=10,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(item.get('ambiente', 'Peça'), weight="bold"),
                            ft.Text(f"{item.get('material', '')} - {item.get('quantidade', 1)}x", size=12, color="grey")
                        ], expand=True),
                        ft.Text(f"R$ {float(item.get('preco_total', 0)):,.2f}", weight="bold", color=COLOR_PRIMARY),
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e, i=idx: remover_peca(i))
                    ])
                )
            )

        conteudo_principal.content = ft.Container(
            padding=20, 
            expand=True, 
            content=ft.Column([
                ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: render_lista_principal()), 
                    ft.Text("Editando Orçamento", size=20, weight="bold"), 
                    ft.Container(expand=True), 
                    ft.ElevatedButton("Salvar Cliente", icon=ft.icons.SAVE, on_click=salvar_cabecalho)
                ]),
                ft.Divider(), 
                ft.Row([txt_edit_nome, txt_edit_cont]),
                txt_edit_end,
                ft.Divider(),
                ft.Row([
                    ft.Text("Peças do Orçamento", size=18, weight="bold"), 
                    ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, bgcolor=COLOR_SECONDARY, color="white", on_click=lambda e: ir_para_calculadora())
                ], alignment="spaceBetween"),
                lista_itens_ui,
                ft.Divider(),
                ft.Row([
                    ft.Text("TOTAL:", size=16, weight="bold"), 
                    ft.Text(f"R$ {total_calc:,.2f}", size=26, weight="bold", color=COLOR_PRIMARY)
                ], alignment="end"),
                ft.Row([
                    ft.OutlinedButton("Gerar PDF", icon=ft.icons.PICTURE_AS_PDF, expand=True, on_click=lambda e: gerar_pdf_orcamento(orc)),
                    ft.ElevatedButton("Mandar Produção", icon=ft.icons.SEND, bgcolor="blue", color="white", expand=True)
                ], spacing=10)
            ])
        )
        page.update()

    def ir_para_calculadora():
        def ao_salvar_item(novo_item):
            estado['orcamento_atual']['itens'].append(novo_item)
            firebase_service.update_document("orcamentos", estado['id_atual'], estado['orcamento_atual'])
            render_tela_editor()
        
        calc = BudgetCalculator(on_save_item=ao_salvar_item, on_cancel=render_tela_editor)
        conteudo_principal.content = calc
        page.update()

    # Inicializa a tela
    render_lista_principal()

    # Retorna o Layout Base com a Sidebar e o Conteúdo Principal
    return ft.View(
        route="/orcamentos",
        padding=0,
        controls=[
            ft.Row([
                Sidebar(page),
                conteudo_principal
            ], expand=True)
        ]
    )