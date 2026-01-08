import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime
import json

def BudgetView(page: ft.Page):
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True, animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT))

    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        def acao_sim(e):
            ao_confirmar()
            page.dialog.open = False
            page.update()
        
        def acao_nao(e):
            page.dialog.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("Cancelar", on_click=acao_nao),
                ft.ElevatedButton("Confirmar", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=acao_sim)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_lista_principal():
        orcamentos = firebase_service.get_collection("orcamentos")
        
        grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
        
        for orc in orcamentos:
            def editar_click(e, o=orc): carregar_editor(o)
            def excluir_click(e, id=orc['id']): 
                mostrar_confirmacao("Excluir Orçamento", "Tem certeza que deseja apagar este orçamento?", lambda: (firebase_service.delete_document("orcamentos", id), render_lista_principal()))

            grid.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    padding=20,
                    bgcolor=COLOR_WHITE,
                    border_radius=BORDER_RADIUS_MD,
                    shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Text(orc.get('cliente_nome', 'Sem Nome'), weight="bold", size=18),
                        ft.Text(f"Data: {orc.get('data', '')}"),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, icon_color=COLOR_PRIMARY, on_click=editar_click),
                            ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=excluir_click),
                        ], alignment="end")
                    ])
                )
            )
        
        conteudo_principal.content = ft.Column([
            ft.Row([
                ft.Text("Orçamentos", size=28, weight="bold", color=COLOR_PRIMARY),
                ft.ElevatedButton("Novo Orçamento", icon=ft.icons.ADD, on_click=lambda _: carregar_editor(None))
            ], alignment="spaceBetween"),
            ft.Divider(),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    def carregar_editor(orc):
        if orc is None:
            estado['orcamento_atual'] = {"cliente_nome": "", "itens": [], "data": datetime.datetime.now().strftime("%d/%m/%Y")}
            estado['id_atual'] = None
        else:
            estado['orcamento_atual'] = orc
            estado['id_atual'] = orc['id']
        render_tela_editor()

    def render_tela_editor():
        orc = estado['orcamento_atual']
        
        # Garante que itens seja uma lista de dicionários (Evita erro de string indices)
        itens_limpos = []
        for i in orc.get('itens', []):
            if isinstance(i, str):
                try: itens_limpos.append(json.loads(i.replace("'", '"')))
                except: continue
            else:
                itens_limpos.append(i)
        orc['itens'] = itens_limpos

        # Cálculo seguro
        total_calc = sum(float(str(i.get('preco_total', 0)).replace(',', '.')) for i in orc['itens'])

        lista_itens = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        for idx, item in enumerate(orc['itens']):
            lista_itens.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{item.get('peca', 'Item')} - {item.get('material', '')}"),
                    subtitle=ft.Text(f"R$ {item.get('preco_total', 0)}"),
                    trailing=ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda e, i=idx: (orc['itens'].pop(idx), render_tela_editor()))
                )
            )

        conteudo_principal.content = ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: render_lista_principal()), ft.Text("Editor de Orçamento", size=20, weight="bold")]),
            ft.TextField(label="Nome do Cliente", value=orc['cliente_nome'], on_change=lambda e: orc.update({"cliente_nome": e.control.value})),
            ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD_BOX, on_click=lambda _: ir_para_calculadora()),
            ft.Divider(),
            ft.Text("Peças Adicionadas:", weight="bold"),
            lista_itens,
            ft.Row([ft.Text("TOTAL:", weight="bold"), ft.Text(f"R$ {total_calc:.2f}", size=24, weight="bold", color=COLOR_PRIMARY)], alignment="end"),
            ft.Row([
                ft.ElevatedButton("Gerar PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, on_click=lambda e: gerar_pdf_orcamento(orc)),
                ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, bgcolor=COLOR_SUCCESS, color=COLOR_WHITE, on_click=lambda e: (firebase_service.update_orcamento(estado['id_atual'], orc) if estado['id_atual'] else firebase_service.add_document("orcamentos", orc), render_lista_principal()))
            ], alignment="end")
        ])
        page.update()

    def ir_para_calculadora():
        def ao_salvar(novo_item):
            estado['orcamento_atual']['itens'].append(novo_item)
            render_tela_editor()
        
        calc = BudgetCalculator(page, on_save_item=ao_salvar, on_cancel=render_tela_editor)
        conteudo_principal.content = calc
        page.update()

    from src.views.layout_base import LayoutBase
    render_lista_principal()
    return LayoutBase(page, conteudo_principal, "Orçamentos")