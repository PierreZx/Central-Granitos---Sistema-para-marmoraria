import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento # <--- Importante: O Serviço de PDF

def BudgetView(page: ft.Page):
    
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True)

    # --- FUNÇÃO AUXILIAR DE CONFIRMAÇÃO ---
    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        def acao_sim(e):
            ao_confirmar()
            dlg.open = False
            page.update()

        def acao_nao(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton("Cancelar", on_click=acao_nao),
                ft.TextButton("Sim, Excluir", style=ft.ButtonStyle(color=ft.colors.RED), on_click=acao_sim),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- LISTA PRINCIPAL (Tela Inicial) ---
    def render_lista_principal():
        lista_dados = firebase_service.get_orcamentos_lista()
        
        grid = ft.GridView(
            expand=True, 
            runs_count=3, 
            max_extent=350, 
            child_aspect_ratio=0.75, 
            spacing=20, 
            run_spacing=20
        )

        if not lista_dados:
            grid.controls.append(ft.Container(content=ft.Column([ft.Icon(ft.icons.REQUEST_QUOTE, size=60, color=ft.colors.GREY_300), ft.Text("Sem orçamentos.", color=ft.colors.GREY_400)], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.center))
        else:
            for orc in lista_dados:
                total = orc.get('total_geral', 0)
                status = orc.get('status', 'Em Aberto')
                cor_st = ft.colors.ORANGE if status == 'Em Aberto' else ft.colors.BLUE if status == 'Produção' else ft.colors.GREEN
                
                card = ft.Container(
                    bgcolor=COLOR_WHITE, border_radius=15, padding=20, shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
                    content=ft.Column([
                        ft.Row([
                            ft.Container(content=ft.Text(status, size=10, color=COLOR_WHITE, weight="bold"), bgcolor=cor_st, padding=5, border_radius=5), 
                            ft.IconButton(ft.icons.MORE_VERT, on_click=lambda e, o=orc: abrir_menu(e, o))
                        ], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', ''), weight="bold", size=18, max_lines=1, overflow="ellipsis"),
                        ft.Text(f"Contato: {orc.get('cliente_contato', '-')}", size=12, color=ft.colors.GREY_600),
                        ft.Text(f"{len(orc.get('itens', []))} itens", size=12, color=ft.colors.GREY_500),
                        ft.Divider(),
                        ft.Row([ft.Text("TOTAL:", weight="bold", size=12), ft.Text(f"R$ {total:.2f}", weight="bold", size=20, color=COLOR_PRIMARY)], alignment="spaceBetween"),
                        ft.Container(height=10),
                        ft.ElevatedButton("Abrir", bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, width=float("inf"), height=45, on_click=lambda e, o=orc: carregar_editor(o))
                    ])
                )
                grid.controls.append(card)

        # Popup para Novo Cliente
        def criar_orc(e):
            if not txt_nome.value: return
            novo = {"cliente_nome": txt_nome.value, "cliente_contato": txt_cont.value, "cliente_endereco": txt_end.value, "itens": [], "total_geral": 0.0, "status": "Em Aberto"}
            res, id_gerado = firebase_service.add_orcamento(novo)
            if res:
                dialog.open = False; novo['id'] = id_gerado; carregar_editor(novo)
        
        txt_nome = ft.TextField(label="Nome"); txt_cont = ft.TextField(label="Contato"); txt_end = ft.TextField(label="Endereço")
        dialog = ft.AlertDialog(title=ft.Text("Novo Cliente"), content=ft.Column([txt_nome, txt_cont, txt_end], tight=True, width=400), actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), ft.ElevatedButton("Criar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=criar_orc)])

        conteudo_principal.content = ft.Container(padding=30, expand=True, content=ft.Column([
            ft.Row([ft.Text("Orçamentos", size=28, weight="bold", color=COLOR_PRIMARY), ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, text="Novo", on_click=lambda e: page.open_dialog(dialog))], alignment="spaceBetween"),
            ft.Divider(), grid
        ]))
        page.update()

    def abrir_menu(e, orc):
        def confirmar_exclusao_orc():
            page.close_bottom_sheet()
            mostrar_confirmacao("Excluir Orçamento?", f"Tem certeza que deseja excluir o orçamento de {orc.get('cliente_nome')}?", lambda: executa_exclusao(orc))

        def executa_exclusao(o):
            firebase_service.delete_orcamento(o['id'])
            page.snack_bar = ft.SnackBar(ft.Text("Orçamento excluído"), bgcolor=ft.colors.RED); page.snack_bar.open = True; page.update(); render_lista_principal() 

        def producao(e):
            page.close_bottom_sheet(); orc['status'] = "Produção"
            firebase_service.update_orcamento(orc['id'], {'status': 'Produção'})
            render_lista_principal()

        page.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column([
            ft.ListTile(leading=ft.Icon(ft.icons.PRECISION_MANUFACTURING), title=ft.Text("Mandar para Produção"), on_click=producao),
            ft.ListTile(leading=ft.Icon(ft.icons.DELETE, color="red"), title=ft.Text("Excluir", color="red"), on_click=lambda e: confirmar_exclusao_orc()),
        ], tight=True), padding=10))
        page.bottom_sheet.open = True
        page.update()

    # --- EDITOR DE ORÇAMENTO (Tela de Detalhes) ---
    def carregar_editor(orcamento):
        estado['orcamento_atual'] = orcamento
        estado['id_atual'] = orcamento.get('id')
        if 'itens' not in estado['orcamento_atual']: estado['orcamento_atual']['itens'] = []
        render_tela_editor()

    def render_tela_editor():
        orc = estado['orcamento_atual']
        txt_nome = ft.TextField(label="Cliente", value=orc.get('cliente_nome'), height=40, text_size=14, expand=True)
        txt_cont = ft.TextField(label="Contato", value=orc.get('cliente_contato'), height=40, text_size=14, expand=True)
        
        def salvar_cli(e):
            orc['cliente_nome'] = txt_nome.value; orc['cliente_contato'] = txt_cont.value
            firebase_service.update_orcamento(estado['id_atual'], orc)
            if e: # Se for chamado pelo botão, mostra snackbar
                page.snack_bar = ft.SnackBar(ft.Text("Dados salvos!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        lista_itens = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        total_calc = sum(i['preco_total'] for i in orc['itens'])
        orc['total_geral'] = total_calc

        # Função para pedir confirmação ao excluir peça
        def click_remover_peca(i):
             mostrar_confirmacao("Remover Peça?", "Deseja remover esta peça?", lambda: executar_remocao_peca(i))

        for idx, item in enumerate(orc['itens']):
            lista_itens.controls.append(ft.Container(
                bgcolor=COLOR_WHITE, padding=15, border_radius=10, border=ft.border.all(1, ft.colors.GREY_200),
                content=ft.Row([
                    ft.Column([ft.Text(item['ambiente'], weight="bold"), ft.Text(f"{item['material']} ({item['largura']}x{item['profundidade']})", size=12, color="grey")], expand=True),
                    ft.Text(f"R$ {item['preco_total']:.2f}", weight="bold", color=COLOR_PRIMARY),
                    ft.IconButton(ft.icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e, i=idx: editar_peca(i)),
                    ft.IconButton(ft.icons.DELETE, icon_color="red", tooltip="Remover", on_click=lambda e, i=idx: click_remover_peca(i))
                ])
            ))

        def executar_remocao_peca(i):
            orc['itens'].pop(i); firebase_service.update_orcamento(estado['id_atual'], orc); render_tela_editor()
            page.snack_bar = ft.SnackBar(ft.Text("Peça removida!"), bgcolor=ft.colors.ORANGE); page.snack_bar.open = True; page.update()

        def editar_peca(i): ir_para_calculadora(item_existente=orc['itens'][i], index_edicao=i)

        # --- AÇÃO DE GERAR PDF ---
        def acao_gerar_pdf(e):
            salvar_cli(None) # Garante que os dados mais recentes do cliente estão no objeto 'orc'
            sucesso = gerar_pdf_orcamento(orc) # Chama o serviço de PDF
            if sucesso:
                page.snack_bar = ft.SnackBar(ft.Text("PDF Gerado e Aberto!"), bgcolor=ft.colors.GREEN)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Erro ao gerar PDF"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

        conteudo_principal.content = ft.Container(padding=20, expand=True, content=ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: render_lista_principal()), ft.Text("Editando Orçamento", size=20, weight="bold"), ft.Container(expand=True), ft.ElevatedButton("Salvar Dados", on_click=salvar_cli, height=40)]),
            ft.Divider(),
            ft.Row([txt_nome, txt_cont]),
            ft.Divider(),
            ft.Row([ft.Text("Peças", size=18, weight="bold"), ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, on_click=lambda e: ir_para_calculadora())], alignment="spaceBetween"),
            lista_itens,
            ft.Divider(),
            ft.Row([ft.Text("TOTAL:", size=16, weight="bold"), ft.Text(f"R$ {total_calc:.2f}", size=26, weight="bold", color=COLOR_PRIMARY)], alignment="end"),
            
            # BOTÕES FINAIS
            ft.Row([
                ft.OutlinedButton("Gerar PDF", icon=ft.icons.PICTURE_AS_PDF, expand=True, on_click=acao_gerar_pdf), 
                ft.ElevatedButton("Mandar para Produção", icon=ft.icons.PRECISION_MANUFACTURING, bgcolor="blue", color="white", expand=True)
            ], spacing=10)
        ]))
        page.update()

    # --- CALCULADORA (Chama o Componente) ---
    def ir_para_calculadora(item_existente=None, index_edicao=None):
        def ao_salvar(novo_item):
            if index_edicao is not None: estado['orcamento_atual']['itens'][index_edicao] = novo_item
            else: estado['orcamento_atual']['itens'].append(novo_item)
            firebase_service.update_orcamento(estado['id_atual'], estado['orcamento_atual'])
            render_tela_editor()
        
        def ao_cancelar(): render_tela_editor()
        
        calc = BudgetCalculator(on_save_item=ao_salvar, on_cancel=ao_cancelar, item_para_editar=item_existente)
        conteudo_principal.content = calc
        page.update()

    # Inicializa na lista
    render_lista_principal()

    return ft.View(route="/orcamentos", padding=0, controls=[ft.Row([Sidebar(page), conteudo_principal], expand=True)])