import flet as ft
from src.views.layout_base import LayoutBase
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_TEXT
from src.services import firebase_service

def DashboardView(page: ft.Page):
    firebase_service.initialize_firebase()
    qtd_estoque = firebase_service.get_collection_count("estoque")
    qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
    faturamento = firebase_service.get_faturamento_mes_atual()
    
    def card_indicador(titulo, valor, icone, cor_icone, cor_valor=COLOR_TEXT):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=45, height=45, border_radius=10,
                        bgcolor=f"{cor_icone}20",
                        content=ft.Icon(icone, color=cor_icone, size=20),
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        # Aplicando Opção B: Uso de TextStyle para propriedades de fonte
                        ft.Text(
                            titulo, 
                            color=ft.colors.GREY_700, 
                            size=12, 
                            style=ft.TextStyle(weight="w500") # Exemplo de uso do style
                        ),
                        ft.Text(
                            valor, 
                            size=20, 
                            color=cor_valor,
                            style=ft.TextStyle(weight="bold") # Centralizando pesos e estilos aqui
                        ),
                    ], spacing=0, expand=True)
                ], alignment="start", spacing=12)
            ]),
            col={"xs": 12, "sm": 6, "md": 4},
            padding=15,
            bgcolor=COLOR_WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color="#00000008"),
        )

    conteudo_corpo = ft.Column([
        # Caso queira usar letter_spacing futuramente, deve ser assim:
        ft.Text(
            "Visão Geral", 
            size=24, 
            color=COLOR_TEXT,
            style=ft.TextStyle(weight="bold", letter_spacing=0.5) 
        ),
        ft.Divider(height=10, color="transparent"),
        
        ft.ResponsiveRow([
            card_indicador("Estoque Total", f"{qtd_estoque} itens", ft.icons.INVENTORY_2, COLOR_INFO),
            card_indicador("Orçamentos", f"{qtd_orcamentos}", ft.icons.DESCRIPTION, COLOR_WARNING),
            card_indicador("Faturamento", f"R$ {faturamento:,.2f}", ft.icons.ATTACH_MONEY, COLOR_SUCCESS, COLOR_SUCCESS),
        ], spacing=15),
        
        ft.Divider(height=20, color="transparent"),
        ft.Text(
            "Ações Rápidas", 
            size=18, 
            color=COLOR_TEXT,
            style=ft.TextStyle(weight="bold")
        ),
        ft.ResponsiveRow([
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.ElevatedButton(
                    "Novo Orçamento", icon=ft.icons.ADD, 
                    bgcolor=COLOR_PRIMARY, color=COLOR_WHITE,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda e: page.go("/orcamentos")
                )
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.ElevatedButton(
                    "Ver Estoque", icon=ft.icons.INVENTORY_2, 
                    bgcolor=COLOR_SECONDARY, color=COLOR_WHITE,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda e: page.go("/estoque")
                )
            ),
        ], spacing=10)
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    return LayoutBase(page, conteudo_corpo, titulo="Marmoraria Central")