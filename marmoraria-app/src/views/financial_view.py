import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, 
    BORDER_RADIUS_LG, BORDER_RADIUS_MD, COLOR_TEXT
)
from src.services import firebase_service
from datetime import datetime

def FinancialView(page: ft.Page):
    
    conteudo_principal = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)
    
    # --- FORMULÁRIOS (TEXTFIELDS) ---
    txt_nome_divida = ft.TextField(label="Nome da Dívida", border_radius=10, filled=True)
    txt_valor_divida = ft.TextField(label="Valor", prefix_text="R$ ", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, filled=True)
    
    def formatar_data(e):
        v = ''.join(filter(str.isdigit, e.control.value))
        if len(v) > 2: v = v[:2] + '/' + v[2:]
        if len(v) > 5: v = v[:5] + '/' + v[5:]
        e.control.value = v[:10]
        e.control.update()

    txt_data_venc = ft.TextField(label="Vencimento", hint_text="DD/MM/AAAA", on_change=formatar_data, border_radius=10, filled=True)
    chk_permanente = ft.Checkbox(label="Conta Fixa Mensal", active_color=COLOR_PRIMARY)
    # CORREÇÃO: Nome padronizado para evitar o erro de 'not defined'
    txt_parcelas = ft.TextField(label="Quantidade de Parcelas", value="1", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, filled=True)

    # --- COMPONENTES DE UI ---
    def criar_kpi_card(titulo, valor, icone, cor, col_size=4):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icone, color=cor, size=30),
                    bgcolor=f"{cor}15", padding=15, border_radius=12
                ),
                ft.Column([
                    ft.Text(titulo, size=13, color=ft.colors.GREY_600, weight="w500"),
                    ft.Text(valor, size=22, weight="bold", color=COLOR_TEXT),
                ], spacing=2)
            ], alignment="start"),
            bgcolor=COLOR_WHITE,
            padding=20,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            col={"xs": 12, "md": col_size}
        )

    def fechar_dialogo(e):
        page.dialog.open = False
        page.update()

    # --- LOGICA DE DADOS ---
    def carregar_dados(e=None):
        conteudo_principal.controls.clear()
        
        # Busca de dados garantindo que não quebre se retornar None
        saldo = firebase_service.get_saldo_caixa() or 0.0
        dividas = firebase_service.get_dividas_pendentes() or []
        receber = firebase_service.get_orcamentos_finalizados_nao_pagos() or []
        extrato = firebase_service.get_extrato_lista() or []

        total_pagar = sum(float(d.get('valor', 0)) for d in dividas)
        total_receber = sum(float(o.get('total_geral', 0)) for o in receber)

        # 1. Header de Resumo
        conteudo_principal.controls.append(
            ft.ResponsiveRow([
                criar_kpi_card("Saldo em Caixa", f"R$ {saldo:,.2f}", ft.icons.ACCOUNT_BALANCE_WALLET_ROUNDED, COLOR_PRIMARY),
                criar_kpi_card("Contas a Pagar", f"R$ {total_pagar:,.2f}", ft.icons.MONEY_OFF_ROUNDED, COLOR_ERROR),
                criar_kpi_card("Contas a Receber", f"R$ {total_receber:,.2f}", ft.icons.ATTACH_MONEY_ROUNDED, COLOR_SUCCESS),
            ], spacing=20)
        )

        # 2. Listas de Abas
        col_pagar = ft.Column(spacing=10)
        for d in dividas: col_pagar.controls.append(criar_item_financeiro(d, "pagar"))

        col_receber = ft.Column(spacing=10)
        for r in receber: col_receber.controls.append(criar_item_financeiro(r, "receber"))

        col_extrato = ft.Column(spacing=8)
        for m in extrato[:15]: col_extrato.controls.append(criar_item_extrato(m))

        tabs = ft.Tabs(
            selected_index=0,
            label_color=COLOR_PRIMARY,
            indicator_color=COLOR_PRIMARY,
            tabs=[
                ft.Tab(text="PAGAR", content=ft.Column([
                    ft.Container(height=10),
                    ft.ElevatedButton("Agendar Conta", icon=ft.icons.ADD, on_click=lambda _: abrir_modal_divida()),
                    col_pagar
                ], scroll=ft.ScrollMode.AUTO)),
                ft.Tab(text="RECEBER", content=col_receber),
                ft.Tab(text="EXTRATO", content=ft.Column([
                    ft.Container(height=10),
                    ft.ElevatedButton("Lançamento Manual", icon=ft.icons.HISTORY_EDU, on_click=lambda _: abrir_modal_manual()),
                    col_extrato
                ], scroll=ft.ScrollMode.AUTO)),
            ],
            expand=True
        )
        
        conteudo_principal.controls.append(tabs)
        page.update()

    def criar_item_financeiro(item, tipo):
        is_pagar = tipo == "pagar"
        nome = item.get('nome') if is_pagar else item.get('cliente_nome', 'Cliente s/ nome')
        valor = float(item.get('valor' if is_pagar else 'total_geral', 0))
        
        return ft.Container(
            content=ft.Row([
                ft.VerticalDivider(width=4, color=COLOR_ERROR if is_pagar else COLOR_SUCCESS, thickness=4),
                ft.Column([
                    ft.Text(nome, weight="bold", size=15),
                    ft.Text(item.get('data_vencimento', 'S/ Data'), size=12, color="grey"),
                ], expand=True),
                ft.Text(f"R$ {valor:,.2f}", weight="bold"),
                ft.IconButton(ft.icons.CHECK_CIRCLE, icon_color=COLOR_SUCCESS, on_click=lambda _: confirmar_pagamento(item, tipo)),
                ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=COLOR_ERROR, on_click=lambda _: deletar_item(item, tipo)) if is_pagar else ft.Container()
            ]),
            bgcolor=COLOR_WHITE, padding=10, border_radius=10, shadow=SHADOW_MD
        )

    def criar_item_extrato(mov):
        is_entrada = mov.get('tipo') == 'Entrada'
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CIRCLE, color=COLOR_SUCCESS if is_entrada else COLOR_ERROR, size=12),
                ft.Column([
                    ft.Text(mov.get('descricao', 'S/ Desc'), size=14, weight="w500"),
                    ft.Text(f"{mov.get('data', '')[:10]} - {mov.get('origem', '')}", size=11, color="grey"),
                ], expand=True),
                ft.Text(f"R$ {float(mov.get('valor', 0)):.2f}", color=COLOR_SUCCESS if is_entrada else COLOR_ERROR, weight="bold")
            ]),
            padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, "#F0F0F0"))
        )

    def abrir_modal_divida():
        txt_nome_divida.value = ""
        txt_valor_divida.value = ""
        txt_data_venc.value = datetime.now().strftime("%d/%m/%Y")
        txt_parcelas.value = "1"
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Nova Conta a Pagar"),
            content=ft.Column([txt_nome_divida, txt_valor_divida, txt_data_venc, txt_parcelas, chk_permanente], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_nova_divida)
            ]
        )
        page.dialog.open = True
        page.update()

    def salvar_nova_divida(e):
        if not txt_nome_divida.value or not txt_valor_divida.value: return
        dados = {
            "nome": txt_nome_divida.value,
            "valor": txt_valor_divida.value.replace(",", "."),
            "data_vencimento": txt_data_venc.value,
            "permanente": chk_permanente.value,
            "parcelas_totais": int(txt_parcelas.value or 1),
            "parcela_atual": 1,
            "status": "Pendente",
            "data_criacao": datetime.now().isoformat()
        }
        firebase_service.add_divida_fixa(dados)
        fechar_dialogo(None)
        carregar_dados()

    def confirmar_pagamento(item, tipo):
        def acao(e):
            if tipo == "pagar": firebase_service.pagar_divida_fixa(item)
            else: firebase_service.receber_orcamento(item)
            fechar_dialogo(None)
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Baixa"),
            content=ft.Text("Deseja confirmar o pagamento/recebimento deste valor?"),
            actions=[ft.TextButton("Não", on_click=fechar_dialogo), ft.ElevatedButton("Sim", on_click=acao)]
        )
        page.dialog.open = True
        page.update()

    def deletar_item(item, tipo):
        firebase_service.delete_divida_fixa(item['id'])
        carregar_dados()

    def abrir_modal_manual():
        dd_tipo = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option("Entrada"), ft.dropdown.Option("Saida")], value="Saida")
        txt_val = ft.TextField(label="Valor", prefix_text="R$ ")
        txt_desc = ft.TextField(label="Descrição")
        
        def salvar(e):
            firebase_service.add_movimentacao(dd_tipo.value, txt_val.value.replace(",","."), txt_desc.value, "Manual")
            fechar_dialogo(None)
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Lançamento Manual"),
            content=ft.Column([dd_tipo, txt_val, txt_desc], tight=True),
            actions=[ft.ElevatedButton("Lançar", on_click=salvar)]
        )
        page.dialog.open = True
        page.update()

    carregar_dados()
    return LayoutBase(page, ft.Container(content=conteudo_principal, padding=20), titulo="Financeiro")