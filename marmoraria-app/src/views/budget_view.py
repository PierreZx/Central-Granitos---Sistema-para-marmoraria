import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, 
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime
import json

def BudgetView(page: ft.Page):
    # Estado local para gerenciar o fluxo sem recarregar a página
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True, animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT))

    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        def acao_sim(e):
            ao_confirmar()
            page.dialog.open = False
            page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.ElevatedButton("Confirmar", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=acao_sim)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_lista_principal():
        orcamentos = firebase_service.get_collection("orcamentos")
        grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
        
        if not orcamentos:
            grid.controls.append(ft.Container(
                content=ft.Text("Nenhum orçamento encontrado.", color=ft.colors.GREY_500),
                padding=50, alignment=ft.alignment.center
            ))

        for orc in orcamentos:
            # Captura de escopo para os botões
            id_orc = orc.get('id')
            
            grid.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    padding=20,
                    bgcolor=COLOR_WHITE,
                    border_radius=BORDER_RADIUS_MD,
                    shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.PERSON, color=COLOR_PRIMARY, size=20),
                            ft.Text(orc.get('cliente_nome', 'Cliente sem nome'), weight="bold", size=16, overflow=ft.TextOverflow.ELLIPSIS),
                        ]),
                        ft.Text(f"📅 {orc.get('data', '--/--/----')}", size=12, color=ft.colors.GREY_700),
                        ft.Divider(height=10, color="transparent"),
                        ft.Row([
                            ft.Text(f"Itens: {len(orc.get('itens', []))}", size=12),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT_ROUNDED, 
                                    icon_color=COLOR_PRIMARY, 
                                    tooltip="Editar",
                                    on_click=lambda e, o=orc: carregar_editor(o)
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE_OUTLINE, 
                                    icon_color=COLOR_ERROR, 
                                    tooltip="Excluir",
                                    on_click=lambda e, i=id_orc: mostrar_confirmacao(
                                        "Excluir Orçamento", 
                                        "Deseja realmente apagar este orçamento?", 
                                        lambda: (firebase_service.delete_document("orcamentos", i), render_lista_principal())
                                    )
                                ),
                            ], spacing=0)
                        ], alignment="spaceBetween")
                    ])
                )
            )
        
        conteudo_principal.content = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Gestão de Orçamentos", size=24, weight="bold", color=COLOR_TEXT),
                    ft.Text("Visualize e edite seus orçamentos ativos", size=14, color=ft.colors.GREY_600),
                ]),
                ft.ElevatedButton(
                    "Novo Orçamento", 
                    icon=ft.icons.ADD, 
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    bgcolor=COLOR_PRIMARY, 
                    color=COLOR_WHITE,
                    on_click=lambda _: carregar_editor(None)
                )
            ], alignment="spaceBetween"),
            ft.Divider(height=30),
            grid
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        page.update()

    def carregar_editor(orc):
        if orc is None:
            estado['orcamento_atual'] = {
                "cliente_nome": "", 
                "cliente_contato": "",
                "cliente_endereco": "",
                "itens": [], 
                "data": datetime.datetime.now().strftime("%d/%m/%Y"),
                "total_geral": 0.0
            }
            estado['id_atual'] = None
        else:
            estado['orcamento_atual'] = orc
            estado['id_atual'] = orc.get('id')
        render_tela_editor()

    def render_tela_editor():
        orc = estado['orcamento_atual']
        
        # Sanitização de itens vindos do banco
        if not isinstance(orc.get('itens'), list):
            orc['itens'] = []

        def remover_item(idx):
            orc['itens'].pop(idx)
            render_tela_editor()

        # Cálculo de Total
        total_calc = 0
        lista_itens_ui = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)
        
        for idx, item in enumerate(orc['itens']):
            try:
                preco = float(str(item.get('preco_total', 0)).replace(',', '.'))
                total_calc += preco
            except: preco = 0

            lista_itens_ui.controls.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(1, "#EEEEEE"),
                    border_radius=8,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"{item.get('ambiente', 'Ambiente')} - {item.get('material', 'Material')}", weight="bold"),
                            ft.Text(f"{item.get('largura')}m x {item.get('profundidade')}m | R$ {preco:,.2f}", size=12),
                        ], expand=True),
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=COLOR_ERROR, on_click=lambda e, i=idx: remover_item(i))
                    ])
                )
            )
        
        orc['total_geral'] = total_calc

        conteudo_principal.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: render_lista_principal()), 
                ft.Text("Editor de Orçamento", size=20, weight="bold")
            ]),
            ft.Container(
                padding=20, bgcolor=COLOR_WHITE, border_radius=10, shadow=SHADOW_MD,
                content=ft.Column([
                    ft.TextField(
                        label="Nome do Cliente", 
                        value=orc['cliente_nome'], 
                        on_change=lambda e: orc.update({"cliente_nome": e.control.value}),
                        border_radius=8
                    ),
                    ft.Row([
                        ft.TextField(label="Contato", expand=1, border_radius=8, value=orc.get('cliente_contato', ''), on_change=lambda e: orc.update({"cliente_contato": e.control.value})),
                        ft.TextField(label="Endereço", expand=2, border_radius=8, value=orc.get('cliente_endereco', ''), on_change=lambda e: orc.update({"cliente_endereco": e.control.value})),
                    ]),
                ], spacing=15)
            ),
            ft.Row([
                ft.Text("Itens do Orçamento", weight="bold", size=18),
                ft.TextButton("Adicionar Peça", icon=ft.icons.ADD_CIRCLE, on_click=lambda _: ir_para_calculadora())
            ], alignment="spaceBetween"),
            lista_itens_ui,
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Text("Total Geral", size=14, color=ft.colors.GREY_600),
                    ft.Text(f"R$ {total_calc:,.2f}", size=28, weight="bold", color=COLOR_PRIMARY),
                ]),
                ft.Row([
                    ft.ElevatedButton(
                        "Gerar PDF", 
                        icon=ft.icons.PICTURE_AS_PDF, 
                        bgcolor=COLOR_SECONDARY, 
                        color=COLOR_WHITE, 
                        on_click=lambda e: gerar_pdf_orcamento(orc)
                    ),
                    ft.ElevatedButton(
                        "Salvar Orçamento", 
                        icon=ft.icons.SAVE, 
                        bgcolor=COLOR_SUCCESS, 
                        color=COLOR_WHITE, 
                        on_click=lambda e: (
                            firebase_service.update_document("orcamentos", estado['id_atual'], orc) if estado['id_atual'] 
                            else firebase_service.add_document("orcamentos", orc),
                            render_lista_principal()
                        )
                    ),
                ], spacing=10)
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO, spacing=20)
        page.update()

    def ir_para_calculadora():
        def ao_salvar(novo_item):
            # Adiciona o novo item à lista local e volta para o editor
            estado['orcamento_atual']['itens'].append(novo_item)
            render_tela_editor()
        
        calc = BudgetCalculator(page, on_save_item=ao_salvar, on_cancel=render_tela_editor)
        conteudo_principal.content = calc
        page.update()

    from src.views.layout_base import LayoutBase
    render_lista_principal()
    return LayoutBase(page, conteudo_principal, "Orçamentos")