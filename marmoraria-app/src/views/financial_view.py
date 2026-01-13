import flet as ft
from datetime import datetime, date
from src.views.layout_base import LayoutBase
from src.services import firebase_service
from src.config import *


def parse_date_br(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y").date()
    except:
        return None


def match_pesquisa(item, termo):
    if not termo:
        return True

    termo = termo.lower()
    for v in item.values():
        if termo in str(v).lower():
            return True
    return False


def FinancialView(page: ft.Page):

    conteudo = ft.Column(expand=True, spacing=15, scroll=ft.ScrollMode.AUTO)
    pesquisa = ft.TextField(
        hint_text="Pesquisar por nome, data ou valor...",
        prefix_icon=ft.icons.SEARCH,
        filled=True
    )

    editando = {"id": None, "tipo": None}

    # ================= CAMPOS =================

    nome = ft.TextField(label="Descrição", filled=True)
    valor = ft.TextField(
        label="Valor",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True
    )
    data = ft.TextField(label="Vencimento (DD/MM/AAAA)", filled=True)
    parcelas = ft.TextField(label="Parcelas", value="1", filled=True)
    fixa = ft.Checkbox(label="Dívida fixa")

    # ================= UTIL =================

    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def confirmar(msg, acao):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmação"),
            content=ft.Text(msg),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=lambda e: (fechar_dialogo(), acao())
                )
            ]
        )
        page.dialog.open = True
        page.update()

    # ================= SALVAR =================

    def salvar_divida(e):
        dados = {
            "descricao": nome.value,
            "valor": float(valor.value.replace(",", ".")),
            "data": data.value,
            "parcelas": int(parcelas.value),
            "tipo": editando["tipo"],
            "fixa": fixa.value,
            "status": "Pendente"
        }

        if editando["id"]:
            firebase_service.update_divida(editando["id"], dados)
        else:
            firebase_service.add_divida(dados)

        editando["id"] = None
        fechar_dialogo()
        carregar()

    # ================= MODAL =================

    def abrir_modal(tipo, item=None):
        editando["tipo"] = tipo
        editando["id"] = item["id"] if item else None

        nome.value = item.get("descricao", "") if item else ""
        valor.value = str(item.get("valor", "")) if item else ""
        data.value = item.get("data", "") if item else ""
        parcelas.value = str(item.get("parcelas", 1)) if item else "1"
        fixa.value = item.get("fixa", False) if item else False

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar" if item else "Novo"),
            content=ft.Column(
                [nome, valor, data, parcelas, fixa],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", on_click=salvar_divida)
            ]
        )
        page.dialog.open = True
        page.update()

    # ================= ITENS =================

    def item_divida(d):
        venc = parse_date_br(d["data"])
        vencida = venc and venc < date.today() and d["status"] == "Pendente"

        return ft.Container(
            padding=10,
            bgcolor=COLOR_WHITE,
            border_radius=10,
            shadow=SHADOW_MD,
            content=ft.Row([
                ft.Icon(
                    ft.icons.PUSH_PIN if d.get("fixa") else ft.icons.CIRCLE,
                    size=14,
                    color=COLOR_PRIMARY if d.get("fixa") else
                    (COLOR_ERROR if vencida else COLOR_SUCCESS)
                ),
                ft.Column([
                    ft.Text(d["descricao"], weight="bold"),
                    ft.Text(d["data"], size=12)
                ], expand=True),
                ft.IconButton(
                    ft.icons.CHECK,
                    on_click=lambda e: firebase_service.pagar_divida(d)
                ),
                ft.IconButton(
                    ft.icons.EDIT,
                    on_click=lambda e: abrir_modal(d["tipo"], d)
                ),
                ft.IconButton(
                    ft.icons.DELETE,
                    icon_color=COLOR_ERROR,
                    on_click=lambda e: confirmar(
                        "Deseja apagar esta dívida?",
                        lambda: (firebase_service.delete_divida(d["id"]), carregar())
                    )
                )
            ])
        )

    def item_extrato(m):
        entrada = m["tipo"] == "Entrada"
        return ft.Container(
            padding=10,
            content=ft.Row([
                ft.Icon(
                    ft.icons.CIRCLE,
                    size=10,
                    color=COLOR_SUCCESS if entrada else COLOR_ERROR
                ),
                ft.Column([
                    ft.Text(m["descricao"]),
                    ft.Text(m["data"], size=11)
                ], expand=True),
                ft.Text(f"R$ {m['valor']:.2f}"),
                ft.IconButton(
                    ft.icons.EDIT,
                    on_click=lambda e: abrir_modal(m["tipo"], m)
                ),
                ft.IconButton(
                    ft.icons.DELETE,
                    icon_color=COLOR_ERROR,
                    on_click=lambda e: confirmar(
                        "Deseja apagar este lançamento?",
                        lambda: (firebase_service.delete_extrato(m["id"]), carregar())
                    )
                )
            ])
        )

    # ================= CARREGAR =================

    def carregar():
        conteudo.controls.clear()

        pagar = firebase_service.get_dividas("Saida")
        receber = firebase_service.get_dividas("Entrada")
        extrato = firebase_service.get_extrato()
        saldo = firebase_service.get_saldo_caixa()
        termo = pesquisa.value

        def ordenar(lista):
            fixas = [d for d in lista if d.get("fixa")]
            normais = [d for d in lista if not d.get("fixa")]
            return fixas + normais

        pagar = ordenar([d for d in pagar if match_pesquisa(d, termo)])
        receber = ordenar([d for d in receber if match_pesquisa(d, termo)])
        extrato = [m for m in extrato if match_pesquisa(m, termo)]

        conteudo.controls.append(
            ft.Column([
                ft.Text(f"Saldo: R$ {saldo:.2f}", weight="bold"),
                pesquisa,
                ft.Row([
                    ft.ElevatedButton(
                        "Novo a Pagar",
                        on_click=lambda e: abrir_modal("Saida")
                    ),
                    ft.ElevatedButton(
                        "Novo a Receber",
                        on_click=lambda e: abrir_modal("Entrada")
                    )
                ])
            ])
        )

        tabs = ft.Tabs(
            tabs=[
                ft.Tab("A PAGAR", ft.Column([item_divida(d) for d in pagar])),
                ft.Tab("A RECEBER", ft.Column([item_divida(d) for d in receber])),
                ft.Tab("EXTRATO", ft.Column([item_extrato(m) for m in extrato]))
            ]
        )

        conteudo.controls.append(tabs)
        page.update()

    pesquisa.on_change = lambda e: carregar()

    carregar()

    return LayoutBase(
        page,
        ft.Container(conteudo, padding=20),
        titulo="Financeiro"
    )
