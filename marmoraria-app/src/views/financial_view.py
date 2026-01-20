# src/views/financial_view.py
import flet as ft
from datetime import datetime, date
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE,
    COLOR_SUCCESS, COLOR_ERROR, SHADOW_MD,
    BORDER_RADIUS_LG, COLOR_TEXT
)
from src.services import firebase_service

# ===================== UTILITÁRIOS DE APOIO =====================

def parse_date_flexivel(data_str):
    """Garante que o app não trave ao ler datas em diferentes formatos (ISO ou BR)."""
    if not data_str: return None
    try:
        if "T" in data_str:
            return datetime.fromisoformat(data_str.split('.')[0]).date()
        return datetime.strptime(data_str.split(' ')[0], "%d/%m/%Y").date()
    except:
        return None

def formatar_data_input(e):
    """Máscara visual para o usuário digitar a data corretamente no celular."""
    nums = "".join(filter(str.isdigit, e.control.value))[:8]
    if len(nums) >= 5:
        e.control.value = f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
    elif len(nums) >= 3:
        e.control.value = f"{nums[:2]}/{nums[2:]}"
    else:
        e.control.value = nums
    e.control.update()

# ===================== VIEW FINANCEIRA =====================

def FinancialView(page: ft.Page):
    # Container que receberá todo o conteúdo dinâmico
    conteudo_scrollable = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    def carregar_dados_financeiros():
        conteudo_scrollable.controls.clear()
        
        try:
            # Puxa os dados que o firebase_service já sincronizou ou buscou no local
            dividas = firebase_service.get_collection("financeiro")
            extrato = firebase_service.get_collection("movimentacoes")
            orcamentos = firebase_service.get_collection("orcamentos")
        except Exception as e:
            conteudo_scrollable.controls.append(
                ft.Container(
                    content=ft.Text(f"Erro de Sincronização: {e}", color=COLOR_ERROR),
                    padding=20, bgcolor=f"{COLOR_ERROR}10", border_radius=10
                )
            )
            page.update()
            return

        hoje = date.today()
        
        # Filtragem de Recebíveis: Orçamentos com status PENDENTE (Produção)
        receber = [o for o in orcamentos if o.get("status") == "PENDENTE"]
        
        # Cálculos Matemáticos dos KPIs
        total_pagar = sum(float(d.get("valor", 0)) for d in dividas if not d.get("pago", False))
        total_receber = sum(float(r.get("total_geral", 0)) for r in receber)
        
        saldo_mes = 0.0
        for m in extrato:
            dt_mov = parse_date_flexivel(m.get("data"))
            if dt_mov and dt_mov.month == hoje.month and dt_mov.year == hoje.year:
                valor = float(m.get("valor", 0))
                if m.get("tipo") == "Entrada":
                    saldo_mes += valor
                else:
                    saldo_mes -= valor

        # --- SEÇÃO 1: CARDS DE RESUMO (KPIs) ---
        conteudo_scrollable.controls.append(
            ft.ResponsiveRow([
                ft.Container(
                    col={"xs": 12, "md": 4},
                    padding=20, bgcolor=COLOR_WHITE, border_radius=BORDER_RADIUS_LG, shadow=SHADOW_MD,
                    content=ft.Row([
                        ft.Icon(ft.icons.MONEY_OFF_ROUNDED, color=COLOR_ERROR, size=30),
                        ft.Column([
                            ft.Text("A PAGAR", color="grey", size=12, weight="bold"),
                            ft.Text(f"R$ {total_pagar:,.2f}", size=20, weight="bold", color=COLOR_ERROR)
                        ], spacing=2)
                    ])
                ),
                ft.Container(
                    col={"xs": 12, "md": 4},
                    padding=20, bgcolor=COLOR_WHITE, border_radius=BORDER_RADIUS_LG, shadow=SHADOW_MD,
                    content=ft.Row([
                        ft.Icon(ft.icons.MONEY_ROUNDED, color=COLOR_SUCCESS, size=30),
                        ft.Column([
                            ft.Text("A RECEBER", color="grey", size=12, weight="bold"),
                            ft.Text(f"R$ {total_receber:,.2f}", size=20, weight="bold", color=COLOR_SUCCESS)
                        ], spacing=2)
                    ])
                ),
                ft.Container(
                    col={"xs": 12, "md": 4},
                    padding=20, bgcolor=COLOR_WHITE, border_radius=BORDER_RADIUS_LG, shadow=SHADOW_MD,
                    content=ft.Row([
                        ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color=COLOR_PRIMARY, size=30),
                        ft.Column([
                            ft.Text("SALDO MÊS", color="grey", size=12, weight="bold"),
                            ft.Text(f"R$ {saldo_mes:,.2f}", size=20, weight="bold", color=COLOR_PRIMARY)
                        ], spacing=2)
                    ])
                ),
            ], spacing=20)
        )

        # --- SEÇÃO 2: ABAS DE GESTÃO DETALHADA ---
        tabs_financeiras = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                # ABA: CONTAS A PAGAR
                ft.Tab(
                    text="PAGAR",
                    icon=ft.icons.PAYMENT_ROUNDED,
                    content=ft.Column([
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Cadastrar Nova Conta", 
                            icon=ft.icons.ADD_ROUNDED, 
                            bgcolor=COLOR_PRIMARY, 
                            color=COLOR_WHITE,
                            height=50,
                            on_click=lambda _: abrir_modal_cadastro_conta()
                        ),
                        ft.Divider(height=20),
                        ft.Column([
                            criar_item_divida(d) for d in dividas if not d.get("pago", False)
                        ], spacing=10)
                    ], scroll=ft.ScrollMode.AUTO, padding=10)
                ),
                # ABA: VALORES A RECEBER (ORÇAMENTOS)
                ft.Tab(
                    text="RECEBER",
                    icon=ft.icons.INCOMING_MAIL_ROUNDED,
                    content=ft.Column([
                        ft.Container(height=10),
                        ft.Text("Valores vinculados a orçamentos em produção", size=12, color="grey", italic=True),
                        ft.Column([
                            criar_item_receber(r) for r in receber
                        ], spacing=10)
                    ], scroll=ft.ScrollMode.AUTO, padding=10)
                ),
                # ABA: HISTÓRICO / EXTRATO
                ft.Tab(
                    text="EXTRATO",
                    icon=ft.icons.RECEIPT_LONG_ROUNDED,
                    content=ft.Column([
                        ft.Container(height=10),
                        ft.Column([
                            criar_item_extrato(m) for m in sorted(extrato, key=lambda x: x.get('data',''), reverse=True)
                        ], spacing=5)
                    ], scroll=ft.ScrollMode.AUTO, padding=10)
                )
            ],
            expand=True
        )
        conteudo_scrollable.controls.append(tabs_financeiras)
        page.update()

    # ===================== COMPONENTES DE LINHA (CARDS) =====================

    def criar_item_divida(d):
        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE, border_radius=10, border=ft.border.all(1, "grey100"),
            content=ft.Row([
                ft.Column([
                    ft.Text(d.get("descricao", "Conta"), weight="bold", color=COLOR_TEXT, size=15),
                    ft.Text(f"Vencimento: {d.get('vencimento', 'N/A')}", size=12, color="grey"),
                ], expand=True),
                ft.Column([
                    ft.Text(f"R$ {float(d.get('valor', 0)):,.2f}", color=COLOR_ERROR, weight="bold", size=15),
                    ft.TextButton(
                        "BAIXAR", 
                        icon=ft.icons.CHECK_CIRCLE_OUTLINE, 
                        font_color=COLOR_SUCCESS,
                        on_click=lambda _: confirmar_baixa(d)
                    )
                ], horizontal_alignment="end")
            ])
        )

    def criar_item_receber(r):
        return ft.Container(
            padding=15, bgcolor=COLOR_WHITE, border_radius=10, border=ft.border.all(1, "grey100"),
            on_click=lambda _: page.go("/orcamentos"),
            content=ft.Row([
                ft.Column([
                    ft.Text(r.get("cliente_nome", "Cliente"), weight="bold", color=COLOR_TEXT),
                    ft.Text(f"ID: {r.get('id', '')[-8:]}", size=11, color="grey"),
                ], expand=True),
                ft.Text(f"R$ {float(r.get('total_geral', 0)):,.2f}", color=COLOR_SUCCESS, weight="bold", size=15),
                ft.Icon(ft.icons.ARROW_FORWARD_IOS_ROUNDED, size=14, color="grey400")
            ])
        )

    def criar_item_extrato(m):
        is_entrada = m.get("tipo") == "Entrada"
        return ft.Container(
            padding=12, border=ft.border.only(bottom=ft.BorderSide(1, "grey50")),
            content=ft.Row([
                ft.Container(
                    width=35, height=35, border_radius=20,
                    bgcolor=f"{COLOR_SUCCESS if is_entrada else COLOR_ERROR}15",
                    content=ft.Icon(
                        ft.icons.ADD_ROUNDED if is_entrada else ft.icons.REMOVE_ROUNDED, 
                        color=COLOR_SUCCESS if is_entrada else COLOR_ERROR, size=20
                    )
                ),
                ft.Column([
                    ft.Text(m.get("descricao", "Movimentação"), size=14, weight="w500", color=COLOR_TEXT),
                    ft.Text(m.get("data", "")[:10], size=11, color="grey"),
                ], expand=True),
                ft.Text(
                    f"{'+' if is_entrada else '-'} R$ {float(m.get('valor', 0)):,.2f}", 
                    color=COLOR_SUCCESS if is_entrada else COLOR_ERROR, weight="bold"
                )
            ])
        )

    # ===================== MODAIS E LÓGICA DE AÇÃO =====================

    def confirmar_baixa(d):
        def realizar_baixa(e):
            d["pago"] = True
            # Salva no banco local/nuvem
            firebase_service.update_document("financeiro", d["id"], d)
            # Gera o registro no extrato automaticamente
            firebase_service.add_movimentacao(
                tipo="Saída",
                valor=float(d.get("valor", 0)),
                descricao=f"PAGTO EFETUADO: {d.get('descricao')}",
                categoria="Despesas"
            )
            page.dialog.open = False
            carregar_dados_financeiros()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Pagamento?"),
            content=ft.Text(f"Deseja marcar '{d.get('descricao')}' como paga?"),
            actions=[
                ft.TextButton("Não", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.ElevatedButton("Sim, Baixar", bgcolor=COLOR_SUCCESS, color=COLOR_WHITE, on_click=realizar_baixa)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_modal_cadastro_conta():
        desc_input = ft.TextField(label="Descrição da Conta", border_radius=10, prefix_icon=ft.icons.DESCRIPTION)
        valor_input = ft.TextField(label="Valor (R$)", border_radius=10, prefix_icon=ft.icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER)
        venc_input = ft.TextField(
            label="Vencimento (DD/MM/AAAA)", 
            border_radius=10, 
            prefix_icon=ft.icons.CALENDAR_MONTH,
            on_change=formatar_data_input
        )

        def salvar_conta(e):
            if not desc_input.value or not valor_input.value:
                return
            
            nova_conta = {
                "descricao": desc_input.value.upper(),
                "valor": float(valor_input.value.replace(",", ".")),
                "vencimento": venc_input.value,
                "pago": False,
                "data_criacao": datetime.now().isoformat()
            }
            firebase_service.add_document("financeiro", nova_conta)
            page.dialog.open = False
            carregar_dados_financeiros()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Nova Conta a Pagar"),
            content=ft.Column([desc_input, valor_input, venc_input], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.ElevatedButton("Salvar Conta", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_conta)
            ]
        )
        page.dialog.open = True
        page.update()

    # Inicialização da View
    carregar_dados_financeiros()

    return LayoutBase(page, conteudo_scrollable, titulo="Financeiro Central")