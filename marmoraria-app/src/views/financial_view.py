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
    
    eh_mobile = page.width < 768
    conteudo_principal = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)
    
    # Variáveis de controle de edição
    editando_divida_id = None
    editando_mov_id = None
    dados_mov_antigos = None

    # --- COMPONENTES DE UI ---
    def criar_kpi_card(titulo, valor, icone, cor, col_size=4):
        """Cria cards de resumo no topo da tela"""
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

    # --- FORMULÁRIOS (TEXTFIELDS) ---
    txt_nome_divida = ft.TextField(label="Nome da Dívida", border_radius=10, filled=True)
    txt_valor_divida = ft.TextField(label="Valor", prefix_text="R$ ", keyboard_type="number", border_radius=10, filled=True)
    
    def formatar_data(e):
        v = ''.join(filter(str.isdigit, e.control.value))
        if len(v) > 2: v = v[:2] + '/' + v[2:]
        if len(v) > 5: v = v[:5] + '/' + v[5:]
        e.control.value = v[:10]
        e.control.update()

    txt_data_venc = ft.TextField(label="Vencimento", hint_text="DD/MM/AAAA", on_change=formatar_data, border_radius=10, filled=True)
    chk_permanente = ft.Checkbox(label="Conta Fixa Mensal", active_color=COLOR_PRIMARY)
    txt_qtd_parcelas = ft.TextField(label="Meses", value="1", keyboard_type="number", border_radius=10, filled=True)

    # --- DIÁLOGOS ---
    def fechar_dialogo(e):
        page.dialog.open = False
        page.update()

    # --- LOGICA DE DADOS ---
    def carregar_dados(e=None):
        conteudo_principal.controls.clear()
        
        # Busca de dados
        saldo = firebase_service.get_saldo_caixa()
        dividas = firebase_service.get_dividas_pendentes()
        receber = firebase_service.get_orcamentos_finalizados_nao_pagos()
        extrato = firebase_service.get_extrato_lista()

        # 1. Header de Resumo (KPIs)
        total_pagar = sum(float(d.get('valor', 0)) for d in dividas)
        total_receber = sum(float(o.get('total_geral', 0)) for o in receber)

        conteudo_principal.controls.append(
            ft.ResponsiveRow([
                criar_kpi_card("Saldo em Caixa", f"R$ {saldo:,.2f}", ft.icons.ACCOUNT_BALANCE_WALLET_ROUNDED, COLOR_PRIMARY),
                criar_kpi_card("Contas a Pagar", f"R$ {total_pagar:,.2f}", ft.icons.MONEY_OFF_ROUNDED, COLOR_ERROR),
                criar_kpi_card("Contas a Receber", f"R$ {total_receber:,.2f}", ft.icons.ATTACH_MONEY_ROUNDED, COLOR_SUCCESS),
            ], spacing=20)
        )

        # 2. Seção de Abas
        col_pagar = ft.Column(spacing=10)
        if not dividas:
            col_pagar.controls.append(ft.Text("Nenhuma conta pendente.", italic=True, color="grey"))
        for d in dividas:
            col_pagar.controls.append(criar_item_financeiro(d, "pagar"))

        col_receber = ft.Column(spacing=10)
        if not receber:
            col_receber.controls.append(ft.Text("Nada a receber no momento.", italic=True, color="grey"))
        for r in receber:
            col_receber.controls.append(criar_item_financeiro(r, "receber"))

        col_extrato = ft.Column(spacing=8)
        for m in extrato[:15]: # Mostra as últimas 15 movimentações
            col_extrato.controls.append(criar_item_extrato(m))

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            label_color=COLOR_PRIMARY,
            unselected_label_color=ft.colors.GREY_600,
            indicator_color=COLOR_PRIMARY,
            tabs=[
                ft.Tab(text="CONTAS A PAGAR", content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    ft.ElevatedButton("Nova Conta", icon=ft.icons.ADD, on_click=lambda _: abrir_modal_divida()),
                    col_pagar
                ]))),
                ft.Tab(text="CONTAS A RECEBER", content=ft.Container(padding=ft.padding.only(top=20), content=col_receber)),
                ft.Tab(text="EXTRATO", content=ft.Container(padding=ft.padding.only(top=20), content=ft.Column([
                    ft.ElevatedButton("Lançamento Manual", icon=ft.icons.HISTORY_EDU, on_click=lambda _: abrir_modal_manual()),
                    col_extrato
                ]))),
            ],
            expand=True
        )
        
        conteudo_principal.controls.append(tabs)
        page.update()

    def criar_item_financeiro(item, tipo):
        """Cria a linha visual para contas a pagar ou receber"""
        is_pagar = tipo == "pagar"
        nome = item.get('nome') if is_pagar else item.get('cliente_nome')
        valor = float(item.get('valor' if is_pagar else 'total_geral', 0))
        
        return ft.Container(
            content=ft.Row([
                ft.VerticalDivider(width=4, color=COLOR_ERROR if is_pagar else COLOR_SUCCESS, thickness=4),
                ft.Column([
                    ft.Text(nome, weight="bold", size=15),
                    ft.Text(item.get('data_vencimento', 'S/ Data') if is_pagar else "Aguardando pagamento", size=12, color="grey"),
                ], expand=True),
                ft.Text(f"R$ {valor:,.2f}", weight="bold", color=COLOR_TEXT),
                ft.IconButton(
                    ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, 
                    icon_color=COLOR_SUCCESS,
                    on_click=lambda _: confirmar_pagamento(item, tipo)
                ),
                ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.GREY_400, on_click=lambda _: deletar_item(item, tipo)) if is_pagar else ft.Container()
            ], spacing=10),
            bgcolor=COLOR_WHITE,
            padding=ft.padding.only(left=0, right=10, top=10, bottom=10),
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=4, color="#00000005")
        )

    def criar_item_extrato(mov):
        """Linha simplificada para o extrato"""
        is_entrada = mov.get('tipo') == 'Entrada'
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.icons.ARROW_UPWARD_ROUNDED if is_entrada else ft.icons.ARROW_DOWNWARD_ROUNDED,
                    color=COLOR_SUCCESS if is_entrada else COLOR_ERROR, size=18
                ),
                ft.Column([
                    ft.Text(mov.get('descricao', 'Sem descrição'), size=14, weight="w500"),
                    ft.Text(f"{mov.get('data', '')[:10]} • {mov.get('origem', '')}", size=11, color="grey"),
                ], expand=True),
                ft.Text(
                    f"{'+' if is_entrada else '-'} R$ {float(mov.get('valor', 0)):.2f}",
                    color=COLOR_SUCCESS if is_entrada else COLOR_ERROR,
                    weight="bold"
                )
            ]),
            padding=10,
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#F0F0F0"))
        )
    
    def deletar_item(item, tipo):
        """Função para excluir uma conta agendada"""
        def confirmar_exclusao(e):
            if tipo == "pagar":
                firebase_service.delete_divida_fixa(item['id'])
            # Se fosse extrato, chamaria a função de estorno
            fechar_dialogo(None)
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Excluir Conta?"),
            content=ft.Text(f"Deseja realmente remover '{item.get('nome')}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Excluir", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=confirmar_exclusao)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_modal_manual():
        """Abre o modal para lançamento de entrada/saída manual no extrato"""
        dd_tipo = ft.Dropdown(
            label="Tipo",
            options=[ft.dropdown.Option("Entrada"), ft.dropdown.Option("Saida")],
            value="Saida", border_radius=10, filled=True
        )
        txt_val = ft.TextField(label="Valor", prefix_text="R$ ", keyboard_type="number", border_radius=10, filled=True)
        txt_desc = ft.TextField(label="Descrição", border_radius=10, filled=True)

        def salvar_extrato(e):
            if not txt_val.value: return
            firebase_service.add_movimentacao(
                tipo=dd_tipo.value,
                valor=txt_val.value.replace(",", "."),
                descricao=txt_desc.value,
                origem="Manual"
            )
            fechar_dialogo(None)
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Lançamento Manual"),
            content=ft.Column([dd_tipo, txt_val, txt_desc], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Lançar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_extrato)
            ]
        )
        page.dialog.open = True
        page.update()

    # --- AÇÕES ---
    def confirmar_pagamento(item, tipo):
        def acao_final(e):
            if tipo == "pagar":
                firebase_service.pagar_divida_fixa(item)
            else:
                firebase_service.receber_orcamento(item)
            fechar_dialogo(None)
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Transação"),
            content=ft.Text(f"Deseja confirmar a baixa deste valor?"),
            actions=[
                ft.TextButton("Voltar", on_click=fechar_dialogo),
                ft.ElevatedButton("Confirmar", bgcolor=COLOR_SUCCESS, color=COLOR_WHITE, on_click=acao_final)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_modal_divida():
        # Limpa campos e abre o modal de nova conta
        txt_nome_divida.value = ""
        txt_valor_divida.value = ""
        txt_data_venc.value = datetime.now().strftime("%d/%m/%Y")
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Agendar Conta"),
            content=ft.Column([txt_nome_divida, txt_valor_divida, txt_data_venc, chk_permanente], tight=True, spacing=15),
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
            "parcelas_totais": 1,
            "parcela_atual": 1
        }
        firebase_service.add_divida_fixa(dados)
        fechar_dialogo(None)
        carregar_dados()

    # Início
    carregar_dados()
    
    return LayoutBase(
        page, 
        ft.Container(content=conteudo_principal, padding=20), 
        titulo="Gestão Financeira"
    )