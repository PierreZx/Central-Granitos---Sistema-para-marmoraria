import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime

def BudgetView(page: ft.Page):
    
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True, animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT))

    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        def acao_sim(e): ao_confirmar(); dlg.open = False; page.update()
        def acao_nao(e): dlg.open = False; page.update()
        dlg = ft.AlertDialog(title=ft.Text(titulo), content=ft.Text(mensagem), actions=[ft.TextButton("Cancelar", on_click=acao_nao), ft.ElevatedButton("Confirmar", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=acao_sim)])
        page.dialog = dlg; dlg.open = True; page.update()

    def enviar_para_producao(orc):
        if orc.get('status') in ["Produção", "Em Andamento", "Finalizado"]: return
        firebase_service.update_orcamento(orc['id'], {'status': 'Produção'})
        firebase_service.descontar_estoque_producao(orc)
        render_lista_principal()
        page.snack_bar = ft.SnackBar(ft.Text("Enviado para produção!"), bgcolor=COLOR_SUCCESS); page.snack_bar.open=True; page.update()

    def render_lista_principal():
        lista_dados = firebase_service.get_orcamentos_lista()
        grid = ft.GridView(expand=True, runs_count=3, max_extent=350, spacing=20, run_spacing=20)

        if not lista_dados:
            grid.controls.append(ft.Container(content=ft.Column([
                ft.Icon(ft.icons.REQUEST_QUOTE, size=50, color=COLOR_PRIMARY),
                ft.Text("Nenhum orçamento", color="grey"),
                ft.ElevatedButton("Criar Novo", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=lambda e: abrir_popup_novo(e))
            ], alignment="center", spacing=10), alignment=ft.alignment.center))
        else:
            for orc in lista_dados:
                total = orc.get('total_geral', 0)
                status = orc.get('status', 'Em Aberto')
                cor_status = COLOR_WARNING if status == 'Em Aberto' else COLOR_PRIMARY if status == 'Produção' else COLOR_SUCCESS
                
                card = ft.Container(
                    bgcolor=COLOR_WHITE, padding=20, border_radius=20, shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(content=ft.Text(status, size=10, color=COLOR_WHITE), bgcolor=cor_status, padding=5, border_radius=5),
                            ft.PopupMenuButton(items=[
                                ft.PopupMenuItem(text="Enviar Produção", on_click=lambda e, o=orc: enviar_para_producao(o)),
                                ft.PopupMenuItem(text="Excluir", on_click=lambda e, o=orc: firebase_service.delete_orcamento(o['id']) or render_lista_principal())
                            ])
                        ], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', ''), weight="bold", size=18, color=COLOR_TEXT),
                        ft.Text(f"R$ {total:.2f}", size=16, weight="bold", color=COLOR_PRIMARY),
                        ft.ElevatedButton("Abrir", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, width=float("inf"), on_click=lambda e, o=orc: carregar_editor(o))
                    ])
                )
                grid.controls.append(card)

        # Header com botão AZUL
        header = ft.Row([
            ft.Text("Orçamentos", size=32, weight="bold", color=COLOR_TEXT),
            ft.ElevatedButton("Novo", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=abrir_popup_novo)
        ], alignment="spaceBetween")

        conteudo_principal.content = ft.Container(padding=30, content=ft.Column([header, ft.Divider(), ft.Container(content=grid, expand=True)]))
        page.update()

    # --- Popup Novo Cliente (Mesmo lógica, cores novas) ---
    txt_nome = ft.TextField(label="Nome do Cliente", border_radius=10)
    txt_cont = ft.TextField(label="Contato", border_radius=10)
    
    dialog = ft.AlertDialog(title=ft.Text("Novo Cliente"), content=ft.Column([txt_nome, txt_cont], tight=True), actions=[
        ft.ElevatedButton("Criar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=lambda e: criar_orc(e))
    ])

    def abrir_popup_novo(e): txt_nome.value = ""; page.dialog = dialog; dialog.open = True; page.update()
    def fechar_popup_novo(): dialog.open = False; page.update()
    def criar_orc(e):
        if not txt_nome.value: return
        res, id_gerado = firebase_service.add_orcamento({"cliente_nome": txt_nome.value, "cliente_contato": txt_cont.value, "itens": [], "total_geral": 0.0, "status": "Em Aberto"})
        if res: fechar_popup_novo(); carregar_editor({"id": id_gerado, "cliente_nome": txt_nome.value, "itens": []})

    def carregar_editor(orcamento):
        estado['orcamento_atual'] = orcamento; estado['id_atual'] = orcamento.get('id')
        if 'itens' not in estado['orcamento_atual']: estado['orcamento_atual']['itens'] = []
        render_tela_editor()

    def render_tela_editor():
        orc = estado['orcamento_atual']
        total_calc = sum(i['preco_total'] for i in orc['itens'])
        orc['total_geral'] = total_calc
        
        lista_itens = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        for idx, item in enumerate(orc['itens']):
            lista_itens.controls.append(ft.Container(
                bgcolor=COLOR_WHITE, padding=15, border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="#00000005"),
                content=ft.Row([
                    ft.Column([ft.Text(item['ambiente'], weight="bold"), ft.Text(f"{item['material']}", size=12, color="grey")]),
                    ft.Text(f"R$ {item['preco_total']:.2f}", weight="bold", color=COLOR_PRIMARY),
                    ft.IconButton(ft.icons.EDIT, icon_color=COLOR_SECONDARY, on_click=lambda e, i=idx: ir_para_calculadora(item_existente=orc['itens'][i], index_edicao=i)),
                    ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, on_click=lambda e, i=idx: remover_item(i))
                ], alignment="spaceBetween")
            ))

        def remover_item(idx): orc['itens'].pop(idx); firebase_service.update_orcamento(estado['id_atual'], orc); render_tela_editor()

        conteudo_principal.content = ft.Container(padding=30, content=ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: render_lista_principal()),
                ft.Text(f"Cliente: {orc.get('cliente_nome')}", size=24, weight="bold", color=COLOR_TEXT)
            ]),
            ft.Divider(),
            ft.Row([ft.Text("Peças", size=18), ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=lambda e: ir_para_calculadora())], alignment="spaceBetween"),
            ft.Container(content=lista_itens, expand=True),
            ft.Divider(),
            ft.Row([ft.Text("TOTAL:", weight="bold"), ft.Text(f"R$ {total_calc:.2f}", size=24, weight="bold", color=COLOR_PRIMARY)], alignment="end"),
            ft.Row([
                ft.ElevatedButton("Gerar PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, on_click=lambda e: gerar_pdf_orcamento(orc)),
                ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, bgcolor=COLOR_SUCCESS, color=COLOR_WHITE, on_click=lambda e: (firebase_service.update_orcamento(estado['id_atual'], orc), render_lista_principal()))
            ], alignment="end")
        ]))
        page.update()

    def ir_para_calculadora(item_existente=None, index_edicao=None):
        def ao_salvar(novo_item):
            if index_edicao is not None: estado['orcamento_atual']['itens'][index_edicao] = novo_item
            else: estado['orcamento_atual']['itens'].append(novo_item)
            firebase_service.update_orcamento(estado['id_atual'], estado['orcamento_atual'])
            render_tela_editor()
        
        calc = BudgetCalculator(page, on_save_item=ao_salvar, on_cancel=render_tela_editor, item_para_editar=item_existente)
        conteudo_principal.content = calc
        page.update()

    render_lista_principal()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo_principal, "Orçamentos")