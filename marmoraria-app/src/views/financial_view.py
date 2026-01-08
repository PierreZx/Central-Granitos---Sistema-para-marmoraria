import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, 
    BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service
from datetime import datetime

def FinancialView(page: ft.Page):
    
    eh_mobile = page.width < 768
    conteudo = ft.Container(expand=True)
    editando_divida_id = None
    editando_mov_id = None
    dados_mov_antigos = None

    # --- CAMPOS DÍVIDA (REMOVIDO EXPAND PARA NÃO DISTORCER NO DIALOG) ---
    txt_nome_divida = ft.TextField(
        label="Nome da Dívida", 
        hint_text="Ex: Compra Serra", 
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )
    
    txt_valor_divida = ft.TextField(
        label="Valor da Parcela", 
        prefix_text="R$ ", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )
    
    def formatar_data(e):
        v = e.control.value
        v = ''.join(filter(str.isdigit, v))
        if len(v) > 2: v = v[:2] + '/' + v[2:]
        if len(v) > 5: v = v[:5] + '/' + v[5:]
        if len(v) > 10: v = v[:10]
        e.control.value = v
        e.control.update()

    txt_data_venc = ft.TextField(
        label="1º Vencimento", 
        hint_text="DD/MM/AAAA", 
        on_change=formatar_data, 
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )
    
    chk_permanente = ft.Checkbox(
        label="Conta Fixa Mensal (Luz, Água)", 
        value=False,
        active_color=COLOR_PRIMARY
    )
    
    txt_qtd_parcelas = ft.TextField(
        label="Duração (Meses)", 
        value="1", 
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Qtd",
        disabled=False,
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )

    def toggle_permanente(e):
        txt_qtd_parcelas.disabled = chk_permanente.value
        if chk_permanente.value: 
            txt_qtd_parcelas.value = "Infinito"
        else: 
            if e is not None: txt_qtd_parcelas.value = "1"
        if txt_qtd_parcelas.page: txt_qtd_parcelas.update()

    chk_permanente.on_change = toggle_permanente

    txt_desc_divida = ft.TextField(
        label="Descrição / PIX (Opcional)", 
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )

    # --- CAMPOS MOVIMENTAÇÃO ---
    txt_valor_mov = ft.TextField(
        label="Valor", 
        prefix_text="R$ ", 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )
    
    dd_tipo_mov = ft.Dropdown(
        label="Tipo", 
        options=[
            ft.dropdown.Option("Entrada", text="Entrada"),
            ft.dropdown.Option("Saida", text="Saída")
        ], 
        value="Saida",
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )
    
    txt_desc_mov = ft.TextField(
        label="Descrição",
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        focused_border_color=COLOR_PRIMARY
    )

    def mostrar_confirmacao(titulo, mensagem, ao_confirmar, tipo="danger"):
        cor_bg = COLOR_ERROR if tipo == "danger" else COLOR_SUCCESS if tipo == "success" else COLOR_WARNING
        dlg_confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=18, weight="bold"),
            content=ft.Column([
                ft.Container(
                    width=60, height=60, border_radius=30, bgcolor=f"{cor_bg}20",
                    content=ft.Icon(
                        ft.icons.WARNING_ROUNDED if tipo == "danger" else ft.icons.INFO_ROUNDED if tipo == "warning" else ft.icons.CHECK_CIRCLE,
                        size=30, color=cor_bg
                    ),
                    alignment=ft.alignment.center, margin=ft.margin.only(bottom=15)
                ),
                ft.Text(mensagem, size=14, text_align="center", color=ft.colors.GREY_700)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=350, tight=True),
            actions=[
                ft.TextButton("Cancelar", style=ft.ButtonStyle(color=ft.colors.GREY_600), on_click=lambda e: fechar_dlg(dlg_confirm)),
                ft.ElevatedButton("Confirmar", style=ft.ButtonStyle(bgcolor=cor_bg, color=COLOR_WHITE, shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: ao_confirmar())
            ],
            shape=ft.RoundedRectangleBorder(radius=20),
        )
        page.dialog = dlg_confirm
        dlg_confirm.open = True
        page.update()

    def fechar_dlg(dlg):
        dlg.open = False
        page.update()

    def carregar_dados():
        saldo = firebase_service.get_saldo_caixa()
        cor_saldo = COLOR_SUCCESS if saldo >= 0 else COLOR_ERROR
        padding_cards = 10 if eh_mobile else 20
        
        card_saldo = ft.Container(
            bgcolor=COLOR_WHITE, padding=padding_cards, border_radius=BORDER_RADIUS_LG, shadow=SHADOW_MD,
            content=ft.Row([
                ft.Container(
                    width=60 if eh_mobile else 80, height=60 if eh_mobile else 80, border_radius=30 if eh_mobile else 40,
                    bgcolor=f"{COLOR_PRIMARY}10", content=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, size=30 if eh_mobile else 40, color=COLOR_PRIMARY),
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text("Saldo em Caixa", size=14, color=ft.colors.GREY_600),
                    ft.Text(f"R$ {saldo:,.2f}", size=28 if eh_mobile else 32, weight="bold", color=cor_saldo)
                ], spacing=2)
            ], spacing=20)
        )

        lista_dividas = firebase_service.get_dividas_pendentes()
        coluna_dividas = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        
        if not lista_dividas:
            coluna_dividas.controls.append(ft.Text("Nenhuma conta a pagar.", color="grey"))
        else:
            hoje = datetime.now().date()
            for div in lista_dividas:
                data_str = div.get('data_vencimento', '')
                try:
                    if "/" in data_str: venc = datetime.strptime(data_str, "%d/%m/%Y").date()
                    else: venc = datetime.strptime(data_str, "%Y-%m-%d").date()
                except: venc = hoje 
                
                delta = (venc - hoje).days
                cor_bola = COLOR_SUCCESS
                msg_prazo = "No prazo"
                if delta < 0: 
                    cor_bola = COLOR_ERROR
                    msg_prazo = f"Venceu há {abs(delta)} dias"
                elif delta == 0: 
                    cor_bola = COLOR_ERROR
                    msg_prazo = "Vence HOJE"
                elif delta <= 7: 
                    cor_bola = COLOR_WARNING
                    msg_prazo = f"Vence em {delta} dias"
                
                texto_parcelas = "Fixa Mensal" if div.get('permanente') else f"Parcela {div.get('parcela_atual', 1)}/{div.get('parcelas_totais', 1)}"
                
                bts = ft.Row([
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, on_click=lambda e, d=div: abrir_add_divida(e, d)),
                    ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED, on_click=lambda e, d=div: deletar_divida(d)),
                    ft.IconButton(ft.icons.CHECK_BOX_OUTLINE_BLANK, icon_color=COLOR_SUCCESS, on_click=lambda e, d=div: acao_pagar_divida(d))
                ], alignment="end")

                if eh_mobile:
                    content_card = ft.Column([
                        ft.Row([
                            ft.Container(width=10, height=10, bgcolor=cor_bola, border_radius=10),
                            ft.Text(div.get('nome', 'Nome'), weight="bold", size=16, expand=True),
                            ft.Text(f"R$ {float(div.get('valor', 0)):.2f}", weight="bold", color=COLOR_ERROR),
                        ]),
                        ft.Row([
                            ft.Icon(ft.icons.CALENDAR_MONTH, size=12, color="grey"),
                            ft.Text(f"{data_str} ({msg_prazo})", size=12, color="grey"),
                            ft.Icon(ft.icons.REPEAT, size=12, color="grey"),
                            ft.Text(texto_parcelas, size=12, color="grey")
                        ]),
                        bts
                    ])
                else:
                    content_card = ft.Row([
                        ft.Container(width=10, height=10, bgcolor=cor_bola, border_radius=10),
                        ft.Column([
                            ft.Text(div.get('nome', 'Nome'), weight="bold"),
                            ft.Text(f"{data_str} | {texto_parcelas}", size=12, color="grey")
                        ], expand=True),
                        ft.Text(f"R$ {float(div.get('valor', 0)):.2f}", weight="bold", color=COLOR_ERROR),
                        bts
                    ])

                coluna_dividas.controls.append(ft.Container(
                    bgcolor=COLOR_WHITE, padding=15, border_radius=BORDER_RADIUS_MD, shadow=SHADOW_MD, content=content_card
                ))

        lista_receber = firebase_service.get_orcamentos_finalizados_nao_pagos()
        coluna_receber = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        
        if not lista_receber: coluna_receber.controls.append(ft.Text("Nada a receber.", color="grey"))
        else:
            for orc in lista_receber:
                btn_rec = ft.IconButton(ft.icons.CHECK_BOX_OUTLINE_BLANK, icon_color=COLOR_SUCCESS, on_click=lambda e, o=orc: acao_receber_orc(o))
                if eh_mobile:
                    c_rec = ft.Column([
                        ft.Row([ft.Text(orc.get('cliente_nome', ''), weight="bold"), ft.Text(f"R$ {orc.get('total_geral', 0):.2f}", weight="bold", color=COLOR_SUCCESS)]),
                        ft.Row([ft.Text("Finalizado", color=COLOR_SUCCESS, size=12), btn_rec], alignment="spaceBetween")
                    ])
                else:
                    c_rec = ft.Row([
                        ft.Icon(ft.icons.RECEIPT_LONG, color=COLOR_PRIMARY),
                        ft.Column([ft.Text(orc.get('cliente_nome', ''), weight="bold"), ft.Text("Finalizado", size=12, color=COLOR_SUCCESS)], expand=True),
                        ft.Text(f"R$ {orc.get('total_geral', 0):.2f}", weight="bold", color=COLOR_SUCCESS),
                        btn_rec
                    ])
                coluna_receber.controls.append(ft.Container(bgcolor=COLOR_WHITE, padding=15, border_radius=BORDER_RADIUS_MD, shadow=SHADOW_MD, content=c_rec))

        lista_extrato = firebase_service.get_extrato_lista()
        coluna_extrato = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        if not lista_extrato: coluna_extrato.controls.append(ft.Text("Sem extrato.", color="grey"))
        else:
            for mov in lista_extrato:
                cor_val = COLOR_SUCCESS if mov.get('tipo') == 'Entrada' else COLOR_ERROR
                sinal = "+" if mov.get('tipo') == 'Entrada' else "-"
                coluna_extrato.controls.append(ft.Container(
                    bgcolor=ft.colors.GREY_50, padding=10, border_radius=5,
                    content=ft.Row([
                        ft.Text(mov.get('data', '')[:10], size=12, color="grey", width=80),
                        ft.Column([ft.Text(mov.get('descricao', ''), weight="bold"), ft.Text(mov.get('origem', ''), size=10)], expand=True),
                        ft.Text(f"{sinal} R$ {float(mov.get('valor', 0)):.2f}", color=cor_val, weight="bold"),
                        ft.PopupMenuButton(items=[
                            ft.PopupMenuItem(text="Editar", on_click=lambda e, m=mov: abrir_add_manual(e, m)),
                            ft.PopupMenuItem(text="Excluir", on_click=lambda e, m=mov: deletar_movimentacao(m))
                        ])
                    ])
                ))

        tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Pagar", content=ft.Container(padding=10, content=ft.Column([ft.ElevatedButton("Nova Conta", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=lambda e: abrir_add_divida(e)), coluna_dividas]))),
            ft.Tab(text="Receber", content=ft.Container(padding=10, content=coluna_receber)),
            ft.Tab(text="Extrato", content=ft.Container(padding=10, content=ft.Column([ft.ElevatedButton("Lançar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=lambda e: abrir_add_manual(e)), coluna_extrato])))
        ], expand=True, label_color=COLOR_PRIMARY, indicator_color=COLOR_PRIMARY)

        conteudo.content = ft.Container(padding=padding_cards, content=ft.Column([
            ft.Row([ft.Text("Financeiro", size=28, weight="bold", color=COLOR_PRIMARY), ft.IconButton(ft.icons.REFRESH, on_click=lambda e: carregar_dados())], alignment="spaceBetween"),
            card_saldo, ft.Divider(), tabs
        ], scroll=ft.ScrollMode.AUTO))
        page.update()

    def deletar_divida(divida):
        def confirmar(): firebase_service.delete_divida_fixa(divida['id']); carregar_dados(); page.snack_bar = ft.SnackBar(ft.Text("Apagado!"), bgcolor=COLOR_ERROR); page.snack_bar.open=True; page.update()
        mostrar_confirmacao("Excluir?", "Confirma?", confirmar)

    def deletar_movimentacao(mov):
        def confirmar(): firebase_service.delete_movimentacao(mov['id'], mov); carregar_dados(); page.snack_bar = ft.SnackBar(ft.Text("Estornado!"), bgcolor=COLOR_WARNING); page.snack_bar.open=True; page.update()
        mostrar_confirmacao("Estornar?", "Isso altera o saldo.", confirmar)

    def acao_pagar_divida(divida):
        def confirmar():
            page.close_dialog()
            firebase_service.pagar_divida_fixa(divida)
            carregar_dados()
            page.snack_bar = ft.SnackBar(ft.Text("Pago!"), bgcolor=COLOR_SUCCESS); page.snack_bar.open=True; page.update()
        mostrar_confirmacao("Pagar?", f"Valor: R$ {divida.get('valor')}", confirmar)

    def acao_receber_orc(orc):
        def confirmar():
            page.close_dialog()
            firebase_service.receber_orcamento(orc)
            carregar_dados()
        mostrar_confirmacao("Receber?", f"Valor: R$ {orc.get('total_geral')}", confirmar)

    def abrir_add_divida(e, divida_existente=None):
        nonlocal editando_divida_id
        if divida_existente:
            editando_divida_id = divida_existente['id']
            txt_nome_divida.value = divida_existente.get('nome', '')
            txt_valor_divida.value = str(divida_existente.get('valor', ''))
            txt_data_venc.value = divida_existente.get('data_vencimento', '')
            chk_permanente.value = divida_existente.get('permanente', False)
            txt_qtd_parcelas.value = str(divida_existente.get('parcelas_totais', 1))
            toggle_permanente(None)
            txt_desc_divida.value = divida_existente.get('descricao', '')
            btn_salvar_divida.text = "Salvar"
        else:
            editando_divida_id = None
            txt_nome_divida.value = ""; txt_valor_divida.value = ""; txt_data_venc.value = ""; txt_desc_divida.value = ""
            chk_permanente.value = False; txt_qtd_parcelas.value = "1"; txt_qtd_parcelas.disabled = False
            btn_salvar_divida.text = "Agendar"
        
        conteudo_dlg = ft.Column([
            txt_nome_divida, 
            txt_valor_divida, 
            txt_data_venc, 
            chk_permanente, 
            txt_qtd_parcelas, 
            txt_desc_divida
        ], tight=True, width=300 if eh_mobile else 400, spacing=15)
        
        dlg_add_divida.content = conteudo_dlg
        page.dialog = dlg_add_divida
        dlg_add_divida.open = True
        page.update()

    def salvar_divida(e):
        if not txt_nome_divida.value: return
        try: qtd = int(txt_qtd_parcelas.value) if txt_qtd_parcelas.value != "Infinito" else 0
        except: qtd = 1
        dados = {
            "nome": txt_nome_divida.value, "valor": txt_valor_divida.value, "data_vencimento": txt_data_venc.value,
            "permanente": chk_permanente.value, "parcelas_totais": qtd, "parcela_atual": 1, "descricao": txt_desc_divida.value
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
        else:
            editando_mov_id = None; dados_mov_antigos = None
            txt_valor_mov.value = ""; txt_desc_mov.value = ""
        
        page.dialog = dlg_add_manual
        dlg_add_manual.open = True
        page.update()

    def salvar_manual(e):
        if not txt_valor_mov.value: return
        dados = {"tipo": dd_tipo_mov.value, "valor": float(txt_valor_mov.value), "descricao": txt_desc_mov.value, "origem": "Manual"}
        if editando_mov_id: firebase_service.update_movimentacao(editando_mov_id, dados_mov_antigos, dados)
        else: firebase_service.add_movimentacao(dd_tipo_mov.value, txt_valor_mov.value, txt_desc_mov.value, "Manual")
        page.close_dialog(); carregar_dados()

    btn_salvar_divida = ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_divida)
    btn_salvar_manual = ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_manual)
    dlg_add_divida = ft.AlertDialog(title=ft.Text("Conta", weight="bold"), actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), btn_salvar_divida])
    
    dlg_add_manual = ft.AlertDialog(
        title=ft.Text("Lançamento", weight="bold"), 
        content=ft.Column([dd_tipo_mov, txt_valor_mov, txt_desc_mov], tight=True, width=300, spacing=15),
        actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), btn_salvar_manual]
    )

    carregar_dados()
    return LayoutBase(page, conteudo, "Financeiro")