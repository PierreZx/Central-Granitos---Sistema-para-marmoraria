import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_BACKGROUND

def DashboardView(page: ft.Page):
    
    # --- Componentes da Dashboard (Cards de KPI) ---
    
    def card_indicador(titulo, valor, icone, cor_icone):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icone, color=cor_icone, size=30),
                    ft.Text(titulo, color=ft.colors.GREY_700, weight="bold")
                ]),
                ft.Text(valor, size=24, weight="bold", color=ft.colors.BLACK)
            ]),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=10,
            width=250, # Largura fixa ou expand
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.1, ft.colors.BLACK))
        )

    # Conteúdo Principal (Lado Direito)
    conteudo = ft.Container(
        expand=True, # ISSO É O SEGREDO: Ocupa todo o espaço que sobra
        padding=30,
        bgcolor=COLOR_BACKGROUND, # Fundo cinza claro para destacar os cards brancos
        content=ft.Column([
            
            # Título da Página
            ft.Text("Visão Geral", size=30, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Bem-vindo ao sistema Central Granitos", color=ft.colors.GREY),
            
            ft.Divider(height=30, color="transparent"),
            
            # Linha de Cards (KPIs)
            ft.Row([
                card_indicador("Faturamento Mensal", "R$ 45.200", ft.Icons.MONETIZATION_ON, "green"),
                card_indicador("Orçamentos Abertos", "12", ft.Icons.DESCRIPTION, "blue"),
                card_indicador("Chapas em Estoque", "340 un", ft.Icons.LAYERS, "orange"),
            ], wrap=True, spacing=20), # wrap=True faz cair pra linha de baixo se faltar espaço
            
            ft.Divider(height=30, color="transparent"),
            
            # Área de Gráfico ou Tabela (Exemplo visual)
            ft.Container(
                bgcolor=ft.colors.WHITE,
                padding=20,
                border_radius=10,
                width=float("inf"), # Ocupa toda a largura disponível
                height=400,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                content=ft.Column([
                    ft.Text("Últimos Orçamentos", weight="bold", size=18),
                    ft.Text("Tabela de dados virá aqui...", color=ft.colors.GREY)
                    # Aqui entraremos com a DataRow depois
                ])
            )
        ], scroll=ft.ScrollMode.AUTO) # Permite rolar se a tela for pequena
    )

    # --- Layout Final: Menu + Conteúdo ---
    return ft.View(
        route="/dashboard",
        padding=0,
        controls=[
            ft.Row(
                controls=[
                    Sidebar(page), # Menu Fixo na Esquerda
                    conteudo       # Conteúdo Expansível na Direita
                ],
                expand=True # A Row principal expande para encher a janela
            )
        ]
    )