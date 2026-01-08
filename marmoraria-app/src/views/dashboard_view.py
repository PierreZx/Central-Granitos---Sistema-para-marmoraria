import flet as ft
from src.views.components.sidebar import Sidebar
from src.views.layout_base import LayoutBase
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_TEXT
from src.services import firebase_service

def DashboardView(page: ft.Page):
    
    firebase_service.initialize_firebase()
    qtd_estoque = firebase_service.get_collection_count("estoque")
    qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
    
    # Busca faturamento real
    faturamento = firebase_service.get_faturamento_mes_atual()
    
    def card_indicador(titulo, valor, icone, cor_icone, cor_valor=COLOR_TEXT):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=50,
                        height=50,
                        border_radius=12,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[f"{cor_icone}15", f"{cor_icone}05"]
                        ),
                        content=ft.Icon(icone, color=cor_icone, size=24),
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text(titulo, color=ft.colors.GREY_600, size=14),
                        ft.Text(valor, size=24, weight="bold", color=cor_valor),
                    ], spacing=0)
                ], alignment="start", spacing=15)
            ]),
            col={"xs": 12, "md": 4},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000005"),
        )

    # Conteúdo principal da Dashboard
    conteudo_corpo = ft.Column([
        ft.Text("Visão Geral", size=28, weight="bold", color=COLOR_TEXT),
        ft.Divider(height=10, color="transparent"),
        
        # Grid de Indicadores
        ft.ResponsiveRow([
            card_indicador("Estoque Total", f"{qtd_estoque} itens", ft.icons.INVENTORY_2, COLOR_INFO),
            card_indicador("Orçamentos", f"{qtd_orcamentos}", ft.icons.DESCRIPTION, COLOR_WARNING),
            card_indicador("Faturamento/Mês", f"R$ {faturamento:,.2f}", ft.icons.ATTACH_MONEY, COLOR_SUCCESS, COLOR_SUCCESS),
        ], spacing=20),
        
        ft.Divider(height=30, color="transparent"),
        
        # Espaço para Gráficos ou Atalhos
        ft.Text("Ações Rápidas", weight="bold", size=20, color=COLOR_TEXT),
        ft.ResponsiveRow([
            ft.Container(
                col={"xs": 6, "md": 3},
                content=ft.ElevatedButton(
                    "Novo Orçamento", icon=ft.icons.ADD, 
                    bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, 
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15),
                    on_click=lambda e: page.go("/orcamentos")
                )
            ),
            ft.Container(
                col={"xs": 6, "md": 3},
                content=ft.ElevatedButton(
                    "Ver Estoque", icon=ft.icons.INVENTORY_2, 
                    bgcolor=COLOR_SECONDARY, color=COLOR_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15),
                    on_click=lambda e: page.go("/estoque")
                )
            ),
        ], spacing=10)
    ], scroll=ft.ScrollMode.AUTO)

    # IMPORTANTE: Retornamos o LayoutBase que agora retorna um Row ou Container, nunca uma View direta.
    return LayoutBase(page, conteudo_corpo, titulo="Dashboard")