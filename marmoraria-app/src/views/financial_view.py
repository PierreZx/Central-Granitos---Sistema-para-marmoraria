import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY
from src.services import firebase_service
from datetime import datetime

def FinancialView(page: ft.Page):
    
    conteudo = ft.Container(expand=True)
    
    # Estados para edição
    editando_divida_id = None
    editando_mov_id = None
    dados_mov_antigos = None

    # --- CAMPOS DÍVIDA ---
    txt_nome_divida = ft.TextField(label="Nome da Dívida (Ex: Compra Serra)", expand=True)
    txt_valor_divida = ft.TextField(label="Valor da Parcela", prefix_text="R$ ", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    
    def formatar_data(e):
        v = e.control.value
        v = ''.join(filter(str.isdigit, v))
        if len(v) > 2: v = v[:2] + '/' + v[2:]
        if len(v) > 5: v = v[:5] + '/' + v[5:]
        if len(v) > 10: v = v[:10]
        e.control.value = v
        e.control.update()

    txt_data_venc = ft.TextField(label="1º Vencimento", hint_text="DD/MM/AAAA", width=160, on_change=formatar_data)
    
    chk_permanente = ft.Checkbox(label="Conta Fixa Mensal (Luz, Água, Aluguel)", value=False)
    
    txt_qtd_parcelas = ft.TextField(
        label="Duração (Meses)", 
        value="1", 
        width=140, 
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Qtd Parcelas",
        disabled=False
    )

    # --- CORREÇÃO AQUI ---
    def toggle_permanente(e):
        txt_qtd_parcelas.disabled = chk_permanente.value
        
        if chk_permanente.value:
            txt_qtd_parcelas.value = "Infinito"
        else:
            # Só reseta para "1" se foi clicado pelo usuário (e não no carregamento)
            if e is not None: 
                txt_qtd_parcelas.value = "1"
        
        # Só atualiza se o componente já estiver na tela
        if txt_qtd_parcelas.page:
            txt_qtd_parcelas.update()

    chk_permanente.on_change = toggle_permanente

    txt_desc_divida = ft.TextField(label="Descrição / Chave PIX (Opcional)")

    # --- CAMPOS MOVIMENTAÇÃO ---
    txt_valor_mov = ft.TextField(label="Valor", prefix_text="R$ ", keyboard_type=ft.KeyboardType.NUMBER)
    dd_tipo_mov = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option("Entrada"), ft.dropdown.Option("Saida")], value="Saida")
    txt_desc_mov = ft.TextField(label="Descrição")

    def mostrar_confirmacao(titulo, mensagem, ao_confirmar):
        dlg_confirm = ft.AlertDialog(
            title=ft.Text(titulo), content=ft.Text(mensagem),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: fechar_dlg(dlg_confirm)), ft.TextButton("Sim", style=ft.ButtonStyle(color=ft.colors.RED), on_click=lambda e: ao_confirmar())]
        )
        page.dialog = dlg_confirm; dlg_confirm.open = True; page.update()

    def fechar_dlg(dlg): dlg.open = False; page.update()

    def carregar_dados():
        saldo = firebase_service.get_saldo_caixa()
        cor_saldo = ft.colors.GREEN if saldo >= 0 else ft.colors.RED
        
        card_saldo = ft.Container(
            bgcolor=COLOR_WHITE, padding=20, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
            content=ft.Row([
                ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, size=40, color=COLOR_PRIMARY),
                ft.Column([ft.Text("Saldo em Caixa", size=14, color=ft.colors.GREY), ft.Text(f"R$ {saldo:.2f}", size=28, weight="bold", color=cor_saldo)])
            ])
        )

        # --- ABA 1: DÍVIDAS ---
        lista_dividas = firebase_service.get_dividas_pendentes()
        coluna_dividas = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        if not lista_dividas: coluna_dividas.controls.append(ft.Text("Nenhuma conta a pagar.", color=ft.colors.GREY))
        else:
            hoje = datetime.now().date()
            for div in lista_dividas:
                data_str = div.get('data_vencimento', '')
                try:
                    if "/" in data_str: venc = datetime.strptime(data_str, "%d/%m/%Y").date()
                    else: venc = datetime.strptime(data_str, "%Y-%m-%d").date()
                except: venc = hoje 
                
                delta = (venc - hoje).days
                cor_bola, tooltip = ft.colors.GREEN, "No prazo"
                if delta < 0: cor_bola, tooltip = ft.colors.RED, f"Venceu há {abs(delta)} dias!"
                elif delta == 0: cor_bola, tooltip = ft.colors.RED, "Vence HOJE!"
                elif delta <= 7: cor_bola, tooltip = ft.colors.AMBER, f"Vence em {delta} dias"
                
                texto_parcelas = ""
                if div.get('permanente'):
                    texto_parcelas = "Fixa Mensal"
                else:
                    total_p = int(div.get('parcelas_totais', 1))
                    atual_p = int(div.get('parcela_atual', 1))
                    if total_p > 1:
                        texto_parcelas = f"Parcela {atual_p}/{total_p}"
                    else:
                        texto_parcelas = "À Vista"

                coluna_dividas.controls.append(ft.Container(
                    bgcolor=COLOR_WHITE, padding=15, border_radius=10, border=ft.border.all(1, ft.colors.GREY_200),
                    content=ft.Row([
                        ft.Container(width=15, height=15, bgcolor=cor_bola, border_radius=15, tooltip=tooltip),
                        ft.Column([
                            ft.Text(div.get('nome', 'Sem Nome'), weight="bold"),
                            ft.Row([
                                ft.Icon(ft.icons.CALENDAR_MONTH, size=14, color="grey"),
                                ft.Text(f"{data_str}", size=12, color="grey"),
                                ft.Container(width=10),
                                ft.Icon(ft.icons.REPEAT, size=14, color=COLOR_PRIMARY if total_p > 1 else "grey"),
                                ft.Text(texto_parcelas, size=12, color=COLOR_PRIMARY if total_p > 1 else "grey", weight="bold")
                            ], spacing=2),
                            ft.Text(div.get('descricao', ''), size=12, italic=True)
                        ], expand=True),
                        ft.Text(f"R$ {float(div.get('valor', 0)):.2f}", weight="bold", color=ft.colors.RED),
                        ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, tooltip="Editar", on_click=lambda e, d=div: abrir_add_divida(e, d)),
                        ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED, tooltip="Excluir", on_click=lambda e, d=div: deletar_divida(d)),
                        ft.IconButton(ft.icons.CHECK_BOX_OUTLINE_BLANK, tooltip="Pagar Parcela", icon_color=ft.colors.GREEN, on_click=lambda e, d=div: acao_pagar_divida(d))
                    ])
                ))

        # --- ABA 2: A RECEBER ---
        lista_receber = firebase_service.get_orcamentos_finalizados_nao_pagos()
        coluna_receber = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        if not lista_receber: coluna_receber.controls.append(ft.Text("Nenhum recebimento pendente.", color=ft.colors.GREY))
        else:
            for orc in lista_receber:
                coluna_receber.controls.append(ft.Container(
                    bgcolor=COLOR_WHITE, padding=15, border_radius=10, border=ft.border.all(1, ft.colors.GREY_200),
                    content=ft.Row([
                        ft.Icon(ft.icons.RECEIPT_LONG, color=COLOR_PRIMARY),
                        ft.Column([ft.Text(orc.get('cliente_nome', 'Cliente'), weight="bold"), ft.Text("Produção Finalizada", size=12, color="green")], expand=True),
                        ft.Text(f"R$ {orc.get('total_geral', 0):.2f}", weight="bold", color=ft.colors.GREEN),
                        ft.IconButton(ft.icons.CHECK_BOX_OUTLINE_BLANK, tooltip="Receber", icon_color=ft.colors.GREEN, on_click=lambda e, o=orc: acao_receber_orc(o))
                    ])
                ))

        # --- ABA 3: EXTRATO ---
        lista_extrato = firebase_service.get_extrato_lista()
        coluna_extrato = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)
        if not lista_extrato: coluna_extrato.controls.append(ft.Text("Sem movimentações.", color=ft.colors.GREY))
        else:
            for mov in lista_extrato:
                cor_val, sinal = (ft.colors.GREEN, "+") if mov.get('tipo') == 'Entrada' else (ft.colors.RED, "-")
                coluna_extrato.controls.append(ft.Container(
                    padding=10, bgcolor=ft.colors.GREY_50, border_radius=5,
                    content=ft.Row([
                        ft.Text(mov.get('data', '')[:10], size=12, color="grey", width=80),
                        ft.Column([ft.Text(mov.get('descricao', ''), weight="bold"), ft.Text(mov.get('origem', ''), size=10, color="grey")], expand=True),
                        ft.Text(f"{sinal} R$ {float(mov.get('valor', 0)):.2f}", color=cor_val, weight="bold"),
                        ft.PopupMenuButton(items=[ft.PopupMenuItem(text="Editar", icon=ft.icons.EDIT, on_click=lambda e, m=mov: abrir_add_manual(e, m)), ft.PopupMenuItem(text="Excluir", icon=ft.icons.DELETE, on_click=lambda e, m=mov: deletar_movimentacao(m))])
                    ])
                ))

        tabs = ft.Tabs(selected_index=0, animation_duration=300, tabs=[
            ft.Tab(text="Contas a Pagar", icon=ft.icons.MONEY_OFF, content=ft.Container(padding=10, content=ft.Column([ft.ElevatedButton("Nova Conta", icon=ft.icons.ADD, on_click=lambda e: abrir_add_divida(e)), coluna_dividas]))),
            ft.Tab(text="A Receber", icon=ft.icons.ATTACH_MONEY, content=ft.Container(padding=10, content=coluna_receber)),
            ft.Tab(text="Extrato", icon=ft.icons.LIST_ALT, content=ft.Container(padding=10, content=ft.Column([ft.ElevatedButton("Lançar Manual", icon=ft.icons.ADD, on_click=lambda e: abrir_add_manual(e)), coluna_extrato])))
        ], expand=True)

        conteudo.content = ft.Container(padding=20, expand=True, content=ft.Column([ft.Text("Financeiro", size=28, weight="bold", color=COLOR_PRIMARY), card_saldo, ft.Divider(), tabs]))
        page.update()

    # --- AÇÕES ---
    def deletar_divida(divida):
        def confirmar(): firebase_service.delete_divida_fixa(divida['id']); carregar_dados(); page.snack_bar = ft.SnackBar(ft.Text("Dívida removida!"), bgcolor=ft.colors.RED); page.snack_bar.open=True; page.update()
        mostrar_confirmacao("Excluir Dívida?", "Tem certeza?", confirmar)

    def deletar_movimentacao(mov):
        def confirmar(): firebase_service.delete_movimentacao(mov['id'], mov); carregar_dados(); page.snack_bar = ft.SnackBar(ft.Text("Estornado!"), bgcolor=ft.colors.ORANGE); page.snack_bar.open=True; page.update()
        mostrar_confirmacao("Estornar?", "Isso corrige o saldo.", confirmar)

    def acao_pagar_divida(divida):
        def confirmar():
            page.close_dialog()
            sucesso, msg = firebase_service.pagar_divida_fixa(divida)
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.colors.GREEN if sucesso else ft.colors.RED); page.snack_bar.open=True; page.update()
            carregar_dados()
        info = f"\n(Parcela {divida.get('parcela_atual')} de {divida.get('parcelas_totais')})" if divida.get('parcelas_totais', 1) > 1 else ""
        mostrar_confirmacao("Pagar Conta?", f"Confirmar pagamento de R$ {divida.get('valor')}?{info}", confirmar)

    def acao_receber_orc(orc):
        def confirmar():
            page.close_dialog()
            firebase_service.receber_orcamento(orc)
            carregar_dados()
        mostrar_confirmacao("Receber?", f"Entrada de R$ {orc.get('total_geral')}?", confirmar)

    # --- FORMULÁRIOS ---
    def abrir_add_divida(e, divida_existente=None):
        nonlocal editando_divida_id
        if divida_existente:
            editando_divida_id = divida_existente['id']
            txt_nome_divida.value = divida_existente.get('nome', '')
            txt_valor_divida.value = str(divida_existente.get('valor', ''))
            txt_data_venc.value = divida_existente.get('data_vencimento', '')
            chk_permanente.value = divida_existente.get('permanente', False)
            
            # CORREÇÃO AQUI: Define estado sem chamar a função que causava erro
            txt_qtd_parcelas.value = str(divida_existente.get('parcelas_totais', 1))
            txt_qtd_parcelas.disabled = chk_permanente.value
            
            txt_desc_divida.value = divida_existente.get('descricao', '')
            dlg_add_divida.title = ft.Text("Editar Conta")
            btn_salvar_divida.text = "Salvar"
        else:
            editando_divida_id = None
            txt_nome_divida.value = ""; txt_valor_divida.value = ""; txt_data_venc.value = ""; txt_desc_divida.value = ""
            chk_permanente.value = False; txt_qtd_parcelas.value = "1"; txt_qtd_parcelas.disabled = False
            dlg_add_divida.title = ft.Text("Nova Conta a Pagar")
            btn_salvar_divida.text = "Agendar"
        page.dialog = dlg_add_divida; dlg_add_divida.open = True; page.update()

    def salvar_divida(e):
        if not txt_nome_divida.value or not txt_valor_divida.value: return
        try: qtd_parc = int(txt_qtd_parcelas.value)
        except: qtd_parc = 1
        dados = {
            "nome": txt_nome_divida.value, "valor": txt_valor_divida.value,
            "data_vencimento": txt_data_venc.value, 
            "permanente": chk_permanente.value, 
            "parcelas_totais": qtd_parc,
            "parcela_atual": 1, 
            "descricao": txt_desc_divida.value
        }
        if editando_divida_id: firebase_service.update_divida_fixa(editando_divida_id, dados)
        else: firebase_service.add_divida_fixa(dados)
        page.close_dialog(); carregar_dados()

    def abrir_add_manual(e, mov_existente=None):
        nonlocal editando_mov_id, dados_mov_antigos
        if mov_existente:
            editando_mov_id = mov_existente['id']; dados_mov_antigos = mov_existente
            dd_tipo_mov.value = mov_existente.get('tipo', 'Saida')
            txt_valor_mov.value = str(mov_existente.get('valor', ''))
            txt_desc_mov.value = mov_existente.get('descricao', '')
            dlg_add_manual.title = ft.Text("Editar")
        else:
            editando_mov_id = None; dados_mov_antigos = None
            txt_valor_mov.value = ""; txt_desc_mov.value = ""
            dlg_add_manual.title = ft.Text("Lançar")
        page.dialog = dlg_add_manual; dlg_add_manual.open = True; page.update()

    def salvar_manual(e):
        if not txt_valor_mov.value: return
        dados = {"tipo": dd_tipo_mov.value, "valor": float(txt_valor_mov.value), "descricao": txt_desc_mov.value, "origem": "Manual"}
        if editando_mov_id: firebase_service.update_movimentacao(editando_mov_id, dados_mov_antigos, dados)
        else: firebase_service.add_movimentacao(dd_tipo_mov.value, txt_valor_mov.value, txt_desc_mov.value, "Manual")
        page.close_dialog(); carregar_dados()

    btn_salvar_divida = ft.ElevatedButton("Agendar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_divida)
    dlg_add_divida = ft.AlertDialog(content=ft.Column([txt_nome_divida, ft.Row([txt_valor_divida, txt_data_venc]), ft.Row([chk_permanente, txt_qtd_parcelas]), txt_desc_divida], tight=True, width=400), actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), btn_salvar_divida])

    dlg_add_manual = ft.AlertDialog(content=ft.Column([dd_tipo_mov, txt_valor_mov, txt_desc_mov], tight=True, width=300), actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_manual)])

    carregar_dados()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Financeiro")