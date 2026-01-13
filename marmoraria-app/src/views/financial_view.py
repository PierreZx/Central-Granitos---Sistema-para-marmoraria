import flet as ft
from datetime import datetime, date
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY,
    COLOR_WHITE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    SHADOW_MD,
    BORDER_RADIUS_LG,
    COLOR_TEXT
)
from src.services import firebase_service


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


def FinancialView(page: ft.Page):

    conteudo = ft.Column(expand=True, spacing=15, scroll=ft.ScrollMode.AUTO)

    # ================= CAMPOS =================

    txt_nome = ft.TextField(label="Nome da Dívida", filled=True)

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

    divida_editando = {"id": None}

    # ================= LÓGICA =================

    def alternar_fixa(e):
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

    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def salvar_divida(e):
        if not txt_nome.value or not txt_valor.value:
            return

        dados = {
            "nome": txt_nome.value,
            "valor": txt_valor.value.replace(",", "."),
            "status": "Pendente",
            "permanente": chk_fixa.value,
            "parcelas_totais": 1 if chk_fixa.value else int(txt_parcelas.value or 1),
            "parcela_atual": 1,
            "data_criacao": datetime.now().isoformat(),
            "tipo": "Saida"
        }

        if chk_fixa.value:
            dados["dia_vencimento"] = int(txt_data.value)
            dados["data_vencimento"] = txt_data.value
        else:
            dados["data_vencimento"] = txt_data.value

        if divida_editando["id"]:
            firebase_service.update_divida_fixa(divida_editando["id"], dados)
        else:
            firebase_service.add_divida_fixa(dados)

        divida_editando["id"] = None
        fechar_dialogo()
        carregar_dados()

    def abrir_modal_divida(div=None):
        divida_editando["id"] = div["id"] if div else None

        txt_nome.value = div.get("nome", "") if div else ""
        txt_valor.value = div.get("valor", "") if div else ""
        txt_data.value = div.get("data_vencimento", "") if div else ""
        txt_parcelas.value = str(div.get("parcelas_totais", 1)) if div else "1"
        chk_fixa.value = div.get("permanente", False) if div else False
        alternar_fixa(None)

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar Conta" if div else "Nova Conta"),
            content=ft.Column(
                [txt_nome, txt_valor, txt_data, txt_parcelas, chk_fixa],
                tight=True,
                spacing=10
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", on_click=salvar_divida)
            ]
        )
        page.dialog.open = True
        page.update()

    def pagar_divida(div):
        firebase_service.pagar_divida_fixa(div)
        carregar_dados()

    def deletar_divida(div):
        firebase_service.delete_divida_fixa(div["id"])
        carregar_dados()

    # ================= UI =================

    def criar_kpi(titulo, valor, cor, icone):
        return ft.Container(
            padding=15,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_LG,
            shadow=SHADOW_MD,
            content=ft.Row([
                ft.Icon(icone, color=cor),
                ft.Column([
                    ft.Text(titulo, size=12, color="grey"),
                    ft.Text(valor, weight="bold", color=COLOR_TEXT)
                ])
            ])
        )

    def criar_item_divida(div):
        venc = parse_date_br(div.get("data_vencimento", ""))
        vencida = venc and venc < date.today() and div.get("status") == "Pendente"

        return ft.Container(
            padding=10,
            bgcolor=COLOR_WHITE,
            border_radius=10,
            shadow=SHADOW_MD,
            content=ft.Row([
                ft.Icon(ft.icons.CIRCLE, size=10,
                        color=COLOR_ERROR if vencida else COLOR_SUCCESS),
                ft.Column([
                    ft.Text(div.get("nome", ""), weight="bold"),
                    ft.Text(div.get("data_vencimento", ""), size=12, color="grey")
                ], expand=True),
                ft.Checkbox(
                    label="Já pagou?",
                    visible=vencida,
                    on_change=lambda e: pagar_divida(div)
                ),
                ft.IconButton(ft.icons.EDIT, on_click=lambda e: abrir_modal_divida(div)),
                ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR,
                              on_click=lambda e: deletar_divida(div))
            ])
        )

    def criar_item_extrato(mov):
        entrada = mov.get("tipo") == "Entrada"
        return ft.Container(
            padding=10,
            content=ft.Row([
                ft.Icon(ft.icons.CIRCLE,
                        size=10,
                        color=COLOR_SUCCESS if entrada else COLOR_ERROR),
                ft.Column([
                    ft.Text(mov.get("descricao", "")),
                    ft.Text(mov.get("data", "")[:10], size=11, color="grey")
                ], expand=True),
                ft.Text(f"R$ {float(mov.get('valor',0)):.2f}",
                        color=COLOR_SUCCESS if entrada else COLOR_ERROR)
            ])
        )

    # ================= CARREGAR =================

    def carregar_dados():
        conteudo.controls.clear()

        saldo = firebase_service.get_saldo_caixa() or 0
        dividas = firebase_service.get_dividas_pendentes() or []
        extrato = firebase_service.get_extrato_lista() or []

        conteudo.controls.append(
            ft.Row([
                criar_kpi("Saldo", f"R$ {saldo:.2f}",
                          COLOR_PRIMARY, ft.icons.ACCOUNT_BALANCE_WALLET),
                criar_kpi("A Pagar", f"{len(dividas)}",
                          COLOR_ERROR, ft.icons.MONEY_OFF)
            ], spacing=10)
        )

        conteudo.controls.append(
            ft.ElevatedButton(
                "Agendar Conta",
                icon=ft.icons.ADD,
                on_click=lambda e: abrir_modal_divida()
            )
        )

        tabs = ft.Tabs(
            tabs=[
                ft.Tab(
                    text="PAGAR",
                    content=ft.Column(
                        [criar_item_divida(d) for d in dividas],
                        spacing=10
                    )
                ),
                ft.Tab(
                    text="EXTRATO",
                    content=ft.Column(
                        [criar_item_extrato(m) for m in extrato],
                        spacing=10
                    )
                )
            ]
        )

        conteudo.controls.append(tabs)
        page.update()

    carregar_dados()

    return LayoutBase(
        page,
        ft.Container(content=conteudo, padding=20),
        titulo="Financeiro"
    )
