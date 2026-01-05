import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.components.budget_calculator import BudgetCalculator
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento

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

    # --- MOSTRAR MOTIVO DO RETORNO ---
    def ver_motivo_retorno(orc):
        motivo = orc.get('motivo_retorno', 'Sem detalhes informados.')
        
        def fechar_motivo(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Atenção: Orçamento Devolvido", color=ft.colors.RED),
            content=ft.Column([
                ft.Icon(ft.icons.WARNING, size=40, color=ft.colors.RED),
                ft.Text("A produção devolveu este item pelo seguinte motivo:", size=12),
                ft.Container(height=10),
                ft.Text(motivo, size=16, weight="bold", color=ft.colors.GREY_800),
                ft.Container(height=10),
                ft.Text("Corrija o erro e envie novamente.", size=12, italic=True)
            ], tight=True, width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[ft.TextButton("Entendi", on_click=fechar_motivo)]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def enviar_para_producao(orc):
            status_atual = orc.get('status', 'Em Aberto')
            if status_atual in ["Produção", "Em Andamento", "Finalizado"]:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Já está em '{status_atual}'!"), bgcolor="orange")
                page.snack_bar.open = True
                page.update()
                return

            # 1. TENTA ATUALIZAR STATUS
            orc['status'] = "Produção"
            orc['motivo_retorno'] = None 
            
            sucesso, msg = firebase_service.update_orcamento(orc['id'], {'status': 'Produção', 'motivo_retorno': None})
            
            if sucesso:
                # 2. SE DEU CERTO, DÁ BAIXA NO ESTOQUE AUTOMATICAMENTE
                try:
                    ok_estoque, msg_estoque = firebase_service.descontar_estoque_producao(orc)
                    if ok_estoque:
                        msg_final = "Enviado para Produção e Estoque Atualizado!"
                    else:
                        msg_final = f"Enviado para Produção, mas erro no estoque: {msg_estoque}"
                except Exception as ex:
                    msg_final = f"Enviado, mas erro crítico no estoque: {ex}"

                page.snack_bar = ft.SnackBar(content=ft.Text(msg_final), bgcolor="blue")
                
                if page.bottom_sheet and page.bottom_sheet.open:
                    page.close_bottom_sheet()
                render_lista_principal()
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro: {msg}"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

    # --- LISTA PRINCIPAL ---
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
                
                cor_st = ft.colors.ORANGE
                icone_alerta = None
                
                if status == 'Produção': cor_st = ft.colors.BLUE
                elif status == 'Em Andamento': cor_st = ft.colors.BLUE_900
                elif status == 'Finalizado': cor_st = ft.colors.GREEN
                elif status == 'Retornado': 
                    cor_st = ft.colors.RED
                    icone_alerta = ft.IconButton(
                        icon=ft.icons.WARNING, 
                        icon_color=ft.colors.RED, 
                        bgcolor=ft.colors.RED_50,
                        tooltip="Ver Motivo da Devolução",
                        on_click=lambda e, o=orc: ver_motivo_retorno(o)
                    )

                linha_topo = [ft.Container(content=ft.Text(status, size=10, color="white", weight="bold"), bgcolor=cor_st, padding=5, border_radius=5)]
                if icone_alerta: linha_topo.append(icone_alerta)
                linha_topo.append(ft.IconButton(ft.icons.MORE_VERT, on_click=lambda e, o=orc: abrir_menu(e, o)))

                card = ft.Container(
                    bgcolor=COLOR_WHITE, border_radius=15, padding=20, shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
                    border=ft.border.all(2, ft.colors.RED) if status == 'Retornado' else None,
                    content=ft.Column([
                        ft.Row(linha_topo, alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', ''), weight="bold", size=18, max_lines=1, overflow="ellipsis"),
                        ft.Text(f"Contato: {orc.get('cliente_contato', '-')}", size=12, color="grey"),
                        ft.Text(f"{len(orc.get('itens', []))} itens", size=12, color="grey"),
                        ft.Divider(),
                        ft.Row([ft.Text("TOTAL:", weight="bold", size=12), ft.Text(f"R$ {total:.2f}", weight="bold", size=20, color=COLOR_PRIMARY)], alignment="spaceBetween"),
                        ft.Container(height=10),
                        ft.ElevatedButton("Abrir / Corrigir" if status == 'Retornado' else "Abrir", bgcolor=COLOR_SECONDARY, color="white", width=float("inf"), height=45, on_click=lambda e, o=orc: carregar_editor(o))
                    ])
                )
                grid.controls.append(card)

        # --- CORREÇÃO DO POPUP NOVO CLIENTE ---
        def criar_orc(e):
            if not txt_nome.value: return
            novo = {"cliente_nome": txt_nome.value, "cliente_contato": txt_cont.value, "cliente_endereco": txt_end.value, "itens": [], "total_geral": 0.0, "status": "Em Aberto"}
            res, id_gerado = firebase_service.add_orcamento(novo)
            if res:
                dialog.open = False
                page.update()
                novo['id'] = id_gerado
                carregar_editor(novo)
        
        def fechar_popup_novo(e):
            dialog.open = False
            page.update()

        def abrir_popup_novo(e):
            # Limpa campos
            txt_nome.value = ""
            txt_cont.value = ""
            txt_end.value = ""
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        txt_nome = ft.TextField(label="Nome")
        txt_cont = ft.TextField(label="Contato")
        txt_end = ft.TextField(label="Endereço")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Novo Cliente"),
            content=ft.Column([txt_nome, txt_cont, txt_end], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_popup_novo),
                ft.ElevatedButton("Criar", bgcolor=COLOR_PRIMARY, color="white", on_click=criar_orc)
            ]
        )

        conteudo_principal.content = ft.Container(padding=30, expand=True, content=ft.Column([
            # CORREÇÃO AQUI: on_click chama abrir_popup_novo
            ft.Row([
                ft.Text("Orçamentos", size=28, weight="bold", color=COLOR_PRIMARY), 
                ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, text="Novo", on_click=abrir_popup_novo)
            ], alignment="spaceBetween"),
            ft.Divider(), 
            grid
        ]))
        page.update()

    def abrir_menu(e, orc):
        def confirma_excluir(): 
            page.close_bottom_sheet()
            mostrar_confirmacao("Excluir?", "Apagar permanentemente?", lambda: excluir(orc))
        
        def excluir(o): 
            firebase_service.delete_orcamento(o['id'])
            render_lista_principal()
            page.snack_bar = ft.SnackBar(ft.Text("Excluído"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            
        def acao_prod(e): 
            enviar_para_producao(orc)

        page.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column([
            ft.ListTile(leading=ft.Icon(ft.icons.PRECISION_MANUFACTURING), title=ft.Text("Mandar para Produção"), on_click=acao_prod),
            ft.ListTile(leading=ft.Icon(ft.icons.DELETE, color="red"), title=ft.Text("Excluir", color="red"), on_click=lambda e: confirma_excluir()),
        ], tight=True), padding=10))
        page.bottom_sheet.open = True
        page.update()

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
            orc['cliente_nome'] = txt_nome.value
            orc['cliente_contato'] = txt_cont.value
            firebase_service.update_orcamento(estado['id_atual'], orc)
            if e: 
                page.snack_bar = ft.SnackBar(ft.Text("Salvo!"), bgcolor="green")
                page.snack_bar.open = True
                page.update()

        lista_itens = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        total_calc = sum(i['preco_total'] for i in orc['itens'])
        orc['total_geral'] = total_calc

        def click_remover(i): mostrar_confirmacao("Remover Peça?", "Confirmar?", lambda: remover(i))
        
        def remover(i): 
            orc['itens'].pop(i)
            firebase_service.update_orcamento(estado['id_atual'], orc)
            render_tela_editor()
            
        def editar(i): 
            ir_para_calculadora(item_existente=orc['itens'][i], index_edicao=i)

        for idx, item in enumerate(orc['itens']):
            lista_itens.controls.append(ft.Container(
                bgcolor=COLOR_WHITE, padding=15, border_radius=10, border=ft.border.all(1, ft.colors.GREY_200),
                content=ft.Row([
                    ft.Column([ft.Text(item['ambiente'], weight="bold"), ft.Text(f"{item['material']} ({item['largura']}x{item['profundidade']})", size=12, color="grey")], expand=True),
                    ft.Text(f"R$ {item['preco_total']:.2f}", weight="bold", color=COLOR_PRIMARY),
                    ft.IconButton(ft.icons.EDIT, icon_color="blue", on_click=lambda e, i=idx: editar(i)),
                    ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, i=idx: click_remover(i))
                ])
            ))

        def acao_pdf(e):
            salvar_cli(None)
            sucesso = gerar_pdf_orcamento(orc)
            page.snack_bar = ft.SnackBar(ft.Text("PDF Gerado!" if sucesso else "Erro PDF"), bgcolor="green" if sucesso else "red")
            page.snack_bar.open = True
            page.update()

        def acao_prod_editor(e): 
            salvar_cli(None)
            enviar_para_producao(orc)

        # Alerta de Retorno
        banner_retorno = ft.Container()
        if orc.get('status') == 'Retornado':
            banner_retorno = ft.Container(
                bgcolor=ft.colors.RED_100, padding=10, border_radius=5, margin=ft.margin.only(bottom=10),
                content=ft.Row([
                    ft.Icon(ft.icons.WARNING, color=ft.colors.RED),
                    ft.Column([
                        ft.Text("Este orçamento foi devolvido pela produção!", weight="bold", color=ft.colors.RED_900),
                        ft.Text(f"Motivo: {orc.get('motivo_retorno', '')}", size=12, color=ft.colors.RED_900)
                    ], expand=True)
                ])
            )

        conteudo_principal.content = ft.Container(padding=20, expand=True, content=ft.Column([
            ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: render_lista_principal()), ft.Text("Editando Orçamento", size=20, weight="bold"), ft.Container(expand=True), ft.ElevatedButton("Salvar Dados", on_click=salvar_cli, height=40)]),
            banner_retorno,
            ft.Divider(), 
            ft.Row([txt_nome, txt_cont]), 
            ft.Divider(),
            ft.Row([ft.Text("Peças", size=18, weight="bold"), ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, bgcolor=COLOR_SECONDARY, color="white", on_click=lambda e: ir_para_calculadora())], alignment="spaceBetween"),
            lista_itens,
            ft.Divider(),
            ft.Row([ft.Text("TOTAL:", size=16, weight="bold"), ft.Text(f"R$ {total_calc:.2f}", size=26, weight="bold", color=COLOR_PRIMARY)], alignment="end"),
            ft.Row([ft.OutlinedButton("Gerar PDF", icon=ft.icons.PICTURE_AS_PDF, expand=True, on_click=acao_pdf), ft.ElevatedButton("Mandar para Produção", icon=ft.icons.PRECISION_MANUFACTURING, bgcolor="blue", color="white", expand=True, on_click=acao_prod_editor)], spacing=10)
        ]))
        page.update()

    def ir_para_calculadora(item_existente=None, index_edicao=None):
        def ao_salvar(novo_item):
            if index_edicao is not None: estado['orcamento_atual']['itens'][index_edicao] = novo_item
            else: estado['orcamento_atual']['itens'].append(novo_item)
            firebase_service.update_orcamento(estado['id_atual'], estado['orcamento_atual'])
            render_tela_editor()
        
        def ao_cancelar(): 
            render_tela_editor()
        
        calc = BudgetCalculator(on_save_item=ao_salvar, on_cancel=ao_cancelar, item_para_editar=item_existente)
        conteudo_principal.content = calc
        page.update()

    render_lista_principal()

        # --- ADAPTAÇÃO MOBILE ---
    from src.views.layout_base import LayoutBase
        # Atenção: Aqui usamos 'conteudo_principal' e o título 'Orçamentos'
    return LayoutBase(page, conteudo_principal, "Orçamentos")