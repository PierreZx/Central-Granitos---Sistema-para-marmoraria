import flet as ft
from src.views.layout_base import LayoutBase
from src.views.components.budget_calculator import BudgetCalculator
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
from src.config import COLOR_PRIMARY, COLOR_WHITE, COLOR_ERROR
import datetime


def BudgetView(page: ft.Page):
    container = ft.Container(expand=True)

    # ===============================
    # VIEW 1 — LISTA
    # ===============================
    def view_lista():
        cards = []

        def novo_orcamento():
            firebase_service.add_document("orcamentos", {
                "cliente_nome": "Novo Cliente",
                "cliente_contato": "",
                "cliente_endereco": "",
                "status": "Em aberto",
                "itens": [],
                "total_geral": 0,
                "data": datetime.datetime.now().isoformat(),
            })
            carregar()

        cards.append(
            ft.ElevatedButton(
                "➕ Novo Orçamento",
                bgcolor=COLOR_PRIMARY,
                color=COLOR_WHITE,
                on_click=lambda e: novo_orcamento()
            )
        )

        for o in firebase_service.get_orcamentos_lista():
            cards.append(
                ft.Container(
                    padding=15,
                    bgcolor=COLOR_WHITE,
                    border_radius=12,
                    content=ft.Column([
                        ft.Text(o["cliente_nome"], weight="bold"),
                        ft.Text(f"R$ {o.get('total_geral',0):,.2f}"),
                        ft.Row([
                            ft.TextButton("Abrir", on_click=lambda e, x=o: view_detalhe(x)),
                            ft.TextButton("PDF", on_click=lambda e, x=o: abrir_pdf(x)),
                        ])
                    ])
                )
            )

        container.content = ft.Column(cards, scroll=ft.ScrollMode.AUTO)
        page.update()

    # ===============================
    # VIEW 2 — DETALHE
    # ===============================
    def view_detalhe(o):
        lista = []

        def recalcular():
            o["total_geral"] = sum(i["preco_total"] for i in o["itens"])
            firebase_service.update_document("orcamentos", o["id"], o)

        for item in o["itens"]:
            lista.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(1, "#ddd"),
                    content=ft.Row([
                        ft.Text(item["ambiente"]),
                        ft.Text(f"R$ {item['preco_total']:,.2f}"),
                        ft.IconButton("edit", on_click=lambda e, it=item: view_calc(o, it)),
                        ft.IconButton("delete", icon_color=COLOR_ERROR,
                                      on_click=lambda e, it=item: remover_item(o, it))
                    ], alignment="spaceBetween")
                )
            )

        container.content = ft.Column([
            ft.Text(o["cliente_nome"], size=22, weight="bold"),
            ft.Column(lista),
            ft.Divider(),
            ft.Row([
                ft.Text(f"Total: R$ {o['total_geral']:,.2f}", size=20),
                ft.ElevatedButton("Adicionar peça",
                                  on_click=lambda e: view_calc(o))
            ], alignment="spaceBetween")
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    # ===============================
    # VIEW 3 — CALCULADORA
    # ===============================
    def view_calc(o, item=None):
        def salvar(peca):
            if item:
                try:
                    idx = o["itens"].index(item)
                    o["itens"][idx] = peca
                except ValueError:
                    o["itens"].append(peca)
            else:
                o["itens"].append(peca)

            o["total_geral"] = sum(i.get("preco_total", 0) for i in o["itens"])
            firebase_service.update_document("orcamentos", o["id"], o)
            view_detalhe(o)

        # Criamos a instância
        calculadora = BudgetCalculator(
            page=page,
            item=item,
            on_save_item=salvar,
            on_cancel=lambda: view_detalhe(o)
        )

        # Limpa e define o novo conteúdo
        container.content = calculadora
        page.update()

    def remover_item(o, item):
        o["itens"].remove(item)
        o["total_geral"] = sum(i["preco_total"] for i in o["itens"])
        firebase_service.update_document("orcamentos", o["id"], o)
        view_detalhe(o)

    def abrir_pdf(o):
        pdf = gerar_pdf_orcamento(o)
        if pdf:
            page.launch_url(f"data:application/pdf;base64,{pdf}")

    def carregar():
        view_lista()

    carregar()
    return LayoutBase(page, container, titulo="Orçamentos")
