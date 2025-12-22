import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_BACKGROUND
from src.services import firebase_service

def DashboardView(page: ft.Page):
    
    # --- 1. Busca de Dados (Backend) ---
    # Inicializa conexão se precisar
    firebase_service.initialize_firebase()
    
    # Busca contagens reais
    qtd_estoque = firebase_service.get_collection_count("estoque")
    qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
    
    # Simulação de faturamento (pois ainda não temos a tabela financeiro completa)
    faturamento_txt = "R$ 0,00" 
    
    # --- 2. Componentes ---

    def card_indicador(titulo, valor, icone, cor_icone, cor_texto=ft.Colors.BLACK):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icone, color=cor_icone, size=30),
                    ft.Text(titulo, color=ft.Colors.GREY_700, weight="bold", size=14)
                ]),
                ft.Text(valor, size=24, weight="bold", color=cor_texto)
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=12,
            width=260,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000010")
        )

    # Área da Tabela de Orçamentos Recentes
    # Se não tiver orçamentos, mostra mensagem cinza
    if qtd_orcamentos == 0:
        conteudo_tabela = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX, size=50, color=ft.Colors.GREY_300),
                ft.Text("Nenhum orçamento registrado ainda.", color=ft.Colors.GREY_400),
                ft.ElevatedButton("Criar Novo Orçamento", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=lambda e: page.go("/orcamentos"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            height=200
        )
    else:
        conteudo_tabela = ft.Text("Aqui entrará a lista de orçamentos (Grid)...", color=ft.Colors.GREY)

    # Conteúdo Principal
    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            
            ft.Text("Visão Geral", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Resumo das atividades da marmoraria", color=ft.Colors.GREY_600),
            
            ft.Divider(height=30, color="transparent"),
            
            # KPIs com DADOS REAIS
            ft.Row([
                card_indicador("Faturamento (Mês)", faturamento_txt, ft.Icons.MONETIZATION_ON, "green"),
                card_indicador("Orçamentos Totais", str(qtd_orcamentos), ft.Icons.DESCRIPTION, "blue"),
                card_indicador("Chapas em Estoque", f"{qtd_estoque} un", ft.Icons.LAYERS, "orange"),
            ], wrap=True, spacing=20),
            
            ft.Divider(height=30, color="transparent"),
            
            # Container da Tabela / Mensagem de Vazio
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=12,
                width=float("inf"),
                height=400, # Altura fixa para o box
                shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
                content=ft.Column([
                    ft.Text("Últimas Movimentações", weight="bold", size=18, color=ft.Colors.GREY_800),
                    ft.Divider(),
                    ft.Container(content=conteudo_tabela, expand=True)
                ])
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    return ft.View(
        route="/dashboard",
        padding=0,
        controls=[
            ft.Row(
                controls=[
                    Sidebar(page), # Menu Lateral
                    conteudo       # Conteúdo
                ],
                expand=True
            )
        ]
    )