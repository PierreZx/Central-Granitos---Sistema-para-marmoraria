import flet as ft
from datetime import datetime, date, timedelta
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_ERROR, BORDER_RADIUS_LG
)
from src.services import firebase_service


def FinancialView(page: ft.Page):

    conteudo = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # ================= UTIL =================

    def hoje():
        return date.today()

    def cor_vencimento(data_str):
        try:
            d = datetime.strptime(data_str, "%d/%m/%Y").date()
            if d < hoje():
                return COLOR_ERROR
            if d <= hoje() + timedelta(days=4):
                return COLOR_WARNING
            return COLOR_SUCCESS
        except:
            return COLOR_SUCCESS

    def fechar_dialogo():
        if page.dialog:
            page.dialog.open = False
            page.update()

    # ================= CONTAS A PAGAR =================

    def marcar_como_pago(div):
        div["status"] = "Pago"
        div["data_pagamento"] = datetime.now().isoformat()

        firebase_service.update_divida_fixa(div["id"], div)

        # lança no extrato
        firebase_service.add_movimentacao(
            "Saida",
            div.get("valor", 0),
            f"Pagamento: {div.get('nome')}",
            "Financeiro"
        )
        carregar()

    def item_divida(div):
        return ft.Container(
            padding=12,
            bgcolor=COLOR_WHITE,
            border_radius=12,
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=10, color=cor_vencimento(div.get("data_vencimento", ""))),
                ft.Column([
                    ft.Text(div.get("nome"), weight="bold"),
                    ft.Text(f"Venc.: {div.get('data_vencimento')}", size=12)
                ], expand=True),
                ft.Text(f"R$ {float(div.get('valor',0)):,.2f}"),
                ft.Checkbox(
                    label="Pago?",
                    visible=div.get("status") != "Pago",
                    on_change=lambda e, d=div: marcar_como_pago(d)
                )
            ])
        )

    # ================= CONTAS A RECEBER =================

    def receber_orcamento(orc, valor_pago):
        saldo = float(orc.get("saldo_restante", orc.get("total_geral", 0)))
        valor = min(valor_pago, saldo)

        novo_saldo = saldo - valor
        orc["saldo_restante"] = novo_saldo
        orc["pago"] = novo_saldo <= 0

        firebase_service.update_document("orcamentos", orc["id"], orc)

        firebase_service.add_movimentacao(
            "Entrada",
            valor,
            f"Receb. Orçamento {orc.get('cliente_nome')}",
            "Vendas"
        )
        carregar()

    def item_receber(orc):
        saldo = float(orc.get("saldo_restante", orc.get("total_geral", 0)))
        txt_valor = ft.TextField(
            value=str(saldo),
            width=120,
            prefix_text="R$ ",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        return ft.Container(
            padding=12,
            bgcolor=COLOR_WHITE,
            border_radius=12,
            content=ft.Row([
                ft.Column([
                    ft.Text(orc.get("cliente_nome"), weight="bold"),
                    ft.Text(f"Saldo: R$ {saldo:,.2f}", size=12)
                ], expand=True),
                txt_valor,
                ft.ElevatedButton(
                    "Receber",
                    on_click=lambda e, o=orc, t=txt_valor:
                        receber_orcamento(o, float(t.value.replace(",", ".")))
                )
            ])
        )

    # ================= EXTRATO =================

    def item_extrato(m):
        cor = COLOR_SUCCESS if m.get("tipo") == "Entrada" else COLOR_ERROR
        return ft.Container(
            padding=10,
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=10, color=cor),
                ft.Column([
                    ft.Text(m.get("descricao"), weight="bold"),
                    ft.Text(m.get("data","")[:10], size=12)
                ], expand=True),
                ft.Text(f"R$ {float(m.get('valor',0)):,.2f}")
            ])
        )

    # ================= CARREGAR =================

    def carregar():
        conteudo.controls.clear()

        saldo = firebase_service.get_saldo_caixa()
        dividas = firebase_service.get_dividas_pendentes()
        receber = firebase_service.get_orcamentos_finalizados_nao_pagos()
        extrato = firebase_service.get_extrato_lista()

        conteudo.controls.append(
            ft.Text(f"Saldo em Caixa: R$ {saldo:,.2f}", size=22, weight="bold", color=COLOR_PRIMARY)
        )

        conteudo.controls.append(ft.Text("Contas a Pagar", weight="bold"))
        conteudo.controls.extend(item_divida(d) for d in dividas)

        conteudo.controls.append(ft.Divider())
        conteudo.controls.append(ft.Text("Contas a Receber", weight="bold"))
        conteudo.controls.extend(item_receber(o) for o in receber)

        conteudo.controls.append(ft.Divider())
        conteudo.controls.append(ft.Text("Extrato", weight="bold"))
        conteudo.controls.extend(item_extrato(m) for m in extrato)

        page.update()

    carregar()
    return LayoutBase(page, conteudo, titulo="Financeiro")
