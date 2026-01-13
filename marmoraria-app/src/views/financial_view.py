import flet as ft
from datetime import datetime, date
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE,
    COLOR_SUCCESS, COLOR_ERROR, SHADOW_MD,
    BORDER_RADIUS_LG, COLOR_TEXT
)
from src.services import firebase_service

# ===================== UTIL =====================

def parse_date_br(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y").date()
    except:
        return None

def formatar_data_seguro(e):
    nums = "".join(filter(str.isdigit, e.control.value))[:8]
    if len(nums) >= 5:
        e.control.value = f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
    elif len(nums) >= 3:
        e.control.value = f"{nums[:2]}/{nums[2:]}"
    else:
        e.control.value = nums
    e.control.update()

# ===================== VIEW =====================

def FinancialView(page: ft.Page):

    conteudo = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # ===================== CAMPOS =====================
    txt_nome = ft.TextField(label="Nome", filled=True)
    txt_valor = ft.TextField(
        label="Valor",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.TEXT,
        input_filter=ft.InputFilter(regex_string=r"[0-9,.]"),
        filled=True
    )
    txt_data = ft.TextField(
        label="Vencimento",
        hint_text="DD/MM/AAAA",
        on_change=formatar_data_seguro,
        filled=True
    )
    txt_parcelas = ft.TextField(
        label="Parcelas",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True
    )
    chk_fixa = ft.Checkbox(label="Conta fixa mensal")

    txt_pesquisa = ft.TextField(
        label="Pesquisar (nome, data ou valor)",
        prefix_icon=ft.icons.SEARCH,
        on_change=lambda e: carregar()
    )

    divida_editando = None
    extrato_editando = None

    # ===================== LÓGICA =====================

    def alternar_fixa(e=None):
        if chk_fixa.value:
            txt_parcelas.disabled = True
            txt_data.label = "Dia do vencimento mensal (1 a 28)"
            txt_data.value = ""
        else:
            txt_parcelas.disabled = False
            txt_data.label = "Vencimento"
            txt_data.value = ""
        page.update()

    chk_fixa.on_change = alternar_fixa

    # ===================== SALVAR =====================

    def salvar_divida(e):
        nonlocal divida_editando

        dados = {
            "nome": txt_nome.value,
            "valor": txt_valor.value.replace(",", "."),
            "permanente": chk_fixa.value,
            "parcelas_totais": 1 if chk_fixa.value else int(txt_parcelas.value or 1),
            "status": "Pendente"
        }

        if chk_fixa.value:
            dados["dia_vencimento"] = int(txt_data.value)
            dados["data_vencimento"] = txt_data.value
        else:
            dados["data_vencimento"] = txt_data.value

        if divida_editando:
            firebase_service.update_divida_fixa(divida_editando["id"], dados)
        else:
            firebase_service.add_divida_fixa(dados)

        fechar_dialogo()
        carregar()

    # ===================== MODAIS =====================

    def abrir_modal_divida(div=None):
        nonlocal divida_editando
        divida_editando = div

        txt_nome.value = div.get("nome", "") if div else ""
        txt_valor.value = str(div.get("valor", "")) if div else ""
        txt_data.value = div.get("data_vencimento", "") if div else ""
        txt_parcelas.value = str(div.get("parcelas_totais", 1)) if div else "1"
        chk_fixa.value = div.get("permanente", False) if div else False

        alternar_fixa()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar Conta" if div else "Nova Conta"),
            content=ft.Column(
                [txt_nome, txt_valor, txt_data, txt_parcelas, chk_fixa],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo()),
                ft.ElevatedButton("Salvar", on_click=salvar_divida)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_confirmacao(texto, acao):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmação"),
            content=ft.Text(texto),
            actions=[
                ft.TextButton("Não", on_click=lambda e: fechar_dialogo()),
                ft.ElevatedButton("Sim", on_click=lambda e: (acao(), fechar_dialogo(), carregar()))
            ]
        )
        page.dialog.open = True
        page.update()

    def fechar_dialogo():
        page.dialog.open = False
        page.update()

    # ===================== ITENS =====================

    def criar_item_divida(div):
        venc = parse_date_br(div.get("data_vencimento", ""))
        vencida = venc and venc < date.today() and div.get("status") == "Pendente"

        return ft.Container(
            padding=10,
            bgcolor=COLOR_WHITE,
            border_radius=10,
            shadow=SHADOW_MD,
            content=ft.Row([
                ft.Icon(ft.icons.CIRCLE, size=10, color=COLOR_ERROR if vencida else COLOR_SUCCESS),
                ft.Column([
                    ft.Text(div.get("nome"), weight="bold"),
                    ft.Text(div.get("data_vencimento", ""), size=12)
                ], expand=True),
                ft.Checkbox(
                    label="Já pagou?",
                    visible=vencida,
                    on_change=lambda e: firebase_service.pagar_divida_fixa(div)
                ),
                ft.IconButton(ft.icons.EDIT, on_click=lambda e: abrir_modal_divida(div)),
                ft.IconButton(
                    ft.icons.DELETE,
                    on_click=lambda e: abrir_confirmacao(
                        "Deseja excluir esta dívida?",
                        lambda: firebase_service.delete_divida_fixa(div["id"])
                    )
                )
            ])
        )

    def criar_item_extrato(m):
        return ft.Container(
            padding=10,
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#eee")),
            content=ft.Row([
                ft.Icon(
                    ft.icons.CIRCLE,
                    size=10,
                    color=COLOR_SUCCESS if m.get("tipo") == "Entrada" else COLOR_ERROR
                ),
                ft.Column([
                    ft.Text(m.get("descricao", ""), weight="bold"),
                    ft.Text(m.get("data", "")[:10], size=12)
                ], expand=True),
                ft.Text(f"R$ {float(m.get('valor',0)):.2f}"),
                ft.IconButton(
                    ft.icons.EDIT,
                    on_click=lambda e: editar_extrato(m)
                ),
                ft.IconButton(
                    ft.icons.DELETE,
                    on_click=lambda e: abrir_confirmacao(
                        "Excluir movimentação?",
                        lambda: firebase_service.delete_movimentacao(m["id"])
                    )
                )
            ])
        )

    # ===================== EXTRATO =====================

    def editar_extrato(m):
        nonlocal extrato_editando
        extrato_editando = m

        txt_valor.value = str(m.get("valor"))
        txt_nome.value = m.get("descricao", "")

        def salvar(e):
            firebase_service.update_movimentacao(
                m["id"],
                {"valor": txt_valor.value, "descricao": txt_nome.value}
            )
            fechar_dialogo()
            carregar()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar Movimentação"),
            content=ft.Column([txt_valor, txt_nome], tight=True),
            actions=[ft.ElevatedButton("Salvar", on_click=salvar)]
        )
        page.dialog.open = True
        page.update()

    # ===================== CARREGAR =====================

    def carregar():
        conteudo.controls.clear()

        saldo = firebase_service.get_saldo_caixa()
        dividas = firebase_service.get_dividas_pendentes()
        receber = firebase_service.get_orcamentos_finalizados_nao_pagos()
        extrato = firebase_service.get_extrato_lista()

        termo = txt_pesquisa.value.lower() if txt_pesquisa.value else ""

        def filtrar(lista):
            if not termo:
                return lista
            return [
                i for i in lista
                if termo in str(i).lower()
            ]

        # KPIs
        conteudo.controls.append(
            ft.ResponsiveRow([
                criar_kpi("Saldo", saldo, COLOR_PRIMARY),
                criar_kpi("A Pagar", sum(float(d.get("valor",0)) for d in dividas), COLOR_ERROR),
                criar_kpi("A Receber", sum(float(r.get("total_geral",0)) for r in receber), COLOR_SUCCESS)
            ])
        )

        tabs = ft.Tabs(
            expand=True,
            tabs=[
                ft.Tab(
                    text="PAGAR",
                    content=ft.Column([
                        txt_pesquisa,
                        ft.ElevatedButton("Nova Conta", on_click=lambda e: abrir_modal_divida()),
                        *[criar_item_divida(d) for d in sorted(filtrar(dividas), key=lambda x: not x.get("permanente", False))]
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text="RECEBER",
                    content=ft.Column([
                        *[
                            ft.Text(f"{r.get('cliente_nome')} - R$ {r.get('total_geral')}")
                            for r in filtrar(receber)
                        ]
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text="EXTRATO",
                    content=ft.Column(
                        [criar_item_extrato(m) for m in filtrar(extrato)],
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            ]
        )

        conteudo.controls.append(tabs)
        page.update()

    def criar_kpi(titulo, valor, cor):
        return ft.Container(
            col={"xs":12,"md":4},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            content=ft.Column([
                ft.Text(titulo, color="grey"),
                ft.Text(f"R$ {valor:,.2f}", size=22, weight="bold", color=cor)
            ])
        )

    carregar()
    return LayoutBase(page, conteudo, titulo="Financeiro")
