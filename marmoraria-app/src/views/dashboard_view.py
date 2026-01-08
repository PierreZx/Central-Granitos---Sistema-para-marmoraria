import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, 
    COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_TEXT, SHADOW_MD,
    COLOR_ERROR
)
from src.services import firebase_service

def DashboardView(page: ft.Page):
    # Container que abrigará o conteúdo principal para permitir trocas de estado (loading/data)
    container_principal = ft.Container(expand=True)

    def criar_card_indicador(titulo, valor, icone, cor_corpo, cor_texto=COLOR_TEXT):
        """Cria um card de métrica (KPI) com design moderno."""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=54, height=54,
                    bgcolor=f"{cor_corpo}15", # Fundo ultra-suave com a cor do tema
                    border_radius=12,
                    content=ft.Icon(icone, color=cor_corpo, size=28),
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(titulo, color=ft.colors.GREY_600, size=13, weight=ft.FontWeight.W_500),
                    ft.Text(valor, size=22, color=cor_texto, weight=ft.FontWeight.BOLD),
                ], spacing=2, expand=True)
            ], alignment=ft.MainAxisAlignment.START, spacing=15),
            col={"xs": 12, "sm": 6, "lg": 4},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=16,
            shadow=SHADOW_MD,
        )

    def carregar_dashboard():
        # Exibe um loader enquanto busca dados
        container_principal.content = ft.Row(
            [ft.ProgressRing(color=COLOR_PRIMARY), ft.Text(" Sincronizando dados...")],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.update()

        try:
            # Busca de dados no Firebase
            firebase_service.initialize_firebase()
            qtd_estoque = firebase_service.get_collection_count("estoque")
            qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
            faturamento = firebase_service.get_faturamento_mes_atual()

            # Montagem da UI com dados reais
            container_principal.content = ft.Column([
                # Cabeçalho de Boas-vindas
                ft.Row([
                    ft.Column([
                        ft.Text("Bem-vindo de volta!", size=28, weight="bold", color=COLOR_TEXT),
                        ft.Text("Aqui está o resumo da sua marmoraria hoje.", size=15, color=ft.colors.GREY_600),
                    ]),
                ], alignment="spaceBetween"),
                
                ft.Divider(height=30, color="transparent"),

                # Grade de Indicadores (KPIs)
                ft.ResponsiveRow([
                    criar_card_indicador("Estoque Total", f"{qtd_estoque} Chapas", ft.icons.INVENTORY_2_ROUNDED, COLOR_INFO),
                    criar_card_indicador("Orçamentos Ativos", f"{qtd_orcamentos}", ft.icons.DESCRIPTION_ROUNDED, COLOR_WARNING),
                    criar_card_indicador("Faturamento/Mês", f"R$ {faturamento:,.2f}", ft.icons.ATTACH_MONEY_ROUNDED, COLOR_SUCCESS, COLOR_SUCCESS),
                ], spacing=20),

                ft.Divider(height=40, color="transparent"),

                # Seção de Atalhos Profissionais
                ft.Text("Ações Rápidas", size=20, weight="bold", color=COLOR_TEXT),
                ft.ResponsiveRow([
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=ft.ElevatedButton(
                            "Novo Orçamento", 
                            icon=ft.icons.ADD_ROUNDED,
                            bgcolor=COLOR_PRIMARY, 
                            color=COLOR_WHITE,
                            height=55,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                            on_click=lambda _: page.go("/orcamentos")
                        )
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=ft.ElevatedButton(
                            "Gerenciar Estoque", 
                            icon=ft.icons.LIST_ALT_ROUNDED,
                            bgcolor=COLOR_WHITE, 
                            color=COLOR_PRIMARY,
                            height=55,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                side={ft.ControlState.DEFAULT: ft.BorderSide(1, COLOR_PRIMARY)}
                            ),
                            on_click=lambda _: page.go("/estoque")
                        )
                    ),
                ], spacing=15),

            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        
        except Exception as e:
            container_principal.content = ft.Text(f"Erro ao carregar dados: {e}", color=COLOR_ERROR)
        
        page.update()

    # Inicia o carregamento
    carregar_dashboard()

    return LayoutBase(page, container_principal, titulo="Dashboard")