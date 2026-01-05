import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_BACKGROUND
from src.services import firebase_service

def DashboardView(page: ft.Page):
    
    firebase_service.initialize_firebase()
    qtd_estoque = firebase_service.get_collection_count("estoque")
    qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
    faturamento_txt = "R$ 0,00" 
    
    def card_indicador(titulo, valor, icone, cor_icone, cor_texto=ft.colors.BLACK):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icone, color=cor_icone, size=30),
                    ft.Text(titulo, color=ft.colors.GREY_700, weight="bold", size=14)
                ]),
                ft.Text(valor, size=24, weight="bold", color=cor_texto)
            ]),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=12,
            width=260,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000010")
        )

    # CORREÇÃO: ft.icons (minúsculo)
    if qtd_orcamentos == 0:
        conteudo_tabela = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.INBOX, size=50, color=ft.colors.GREY_300),
                ft.Text("Nenhum orçamento registrado ainda.", color=ft.colors.GREY_400),
                ft.ElevatedButton("Criar Novo Orçamento", bgcolor=COLOR_PRIMARY, color=ft.colors.WHITE, on_click=lambda e: page.go("/orcamentos"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            height=200
        )
    else:
        conteudo_tabela = ft.Text("Aqui entrará a lista de orçamentos (Grid)...", color=ft.colors.GREY)

    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Visão Geral", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Resumo das atividades da marmoraria", color=ft.colors.GREY_600),
            ft.Divider(height=30, color="transparent"),
            ft.Row([
                # CORREÇÃO: ft.icons
                card_indicador("Faturamento (Mês)", faturamento_txt, ft.icons.MONETIZATION_ON, "green"),
                card_indicador("Orçamentos Totais", str(qtd_orcamentos), ft.icons.DESCRIPTION, "blue"),
                card_indicador("Chapas em Estoque", f"{qtd_estoque} un", ft.icons.LAYERS, "orange"),
            ], wrap=True, spacing=20),
            ft.Divider(height=30, color="transparent"),
            ft.Container(
                bgcolor=ft.colors.WHITE,
                padding=20,
                border_radius=12,
                width=float("inf"),
                height=400, 
                shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
                content=ft.Column([
                    ft.Text("Últimas Movimentações", weight="bold", size=18, color=ft.colors.GREY_800),
                    ft.Divider(),
                    ft.Container(content=conteudo_tabela, expand=True)
                ])
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Dashboard")