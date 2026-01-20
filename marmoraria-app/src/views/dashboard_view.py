# src/views/dashboard_view.py
import flet as ft
from datetime import datetime
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY, COLOR_WHITE, COLOR_SUCCESS, 
    COLOR_WARNING, COLOR_INFO, COLOR_TEXT, SHADOW_MD,
    COLOR_ERROR
)
from src.services import firebase_service

def DashboardView(page: ft.Page):
    container_principal = ft.Container(expand=True)

    # ===================== CARD KPI =====================
    def criar_card_indicador(titulo, valor, icone, cor_corpo, cor_texto=COLOR_TEXT):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=54,
                    height=54,
                    bgcolor=f"{cor_corpo}15",
                    border_radius=12,
                    alignment=ft.alignment.center,
                    content=ft.Icon(icone, color=cor_corpo, size=28),
                ),
                ft.Column([
                    ft.Text(titulo, size=13, color=ft.colors.GREY_600, weight=ft.FontWeight.W_500),
                    ft.Text(valor, size=22, weight=ft.FontWeight.BOLD, color=cor_texto),
                ], spacing=2, expand=True)
            ], spacing=15),
            col={"xs": 12, "sm": 6, "lg": 4},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=16,
            shadow=SHADOW_MD,
        )

    # ===================== FATURAMENTO =====================
    def calcular_faturamento_mes_atual():
        # Ajustado para usar 'movimentacoes' que existe no seu service
        movimentacoes = firebase_service.get_collection("movimentacoes")
        hoje = datetime.now()
        total = 0.0

        for mov in movimentacoes:
            try:
                if mov.get("tipo") != "Entrada":
                    continue
                
                # Tratamento de data flexível para evitar crash
                data_str = mov.get("data", "")
                if not data_str: continue
                
                # Tenta converter o formato do Firebase ou do SQLite
                if "T" in data_str: # ISO format
                    data_mov = datetime.fromisoformat(data_str.split('.')[0])
                else: # Formato DD/MM/YYYY
                    data_mov = datetime.strptime(data_str.split(' ')[0], "%d/%m/%Y")

                if data_mov.month == hoje.month and data_mov.year == hoje.year:
                    total += float(mov.get("valor", 0))
            except Exception as e:
                print(f"Erro ao processar data na dash: {e}")
                continue

        return total

    # ===================== CARREGAR DASH =====================
    def carregar_dashboard():
        container_principal.content = ft.Row(
            [
                ft.ProgressRing(color=COLOR_PRIMARY),
                ft.Text(" Carregando dados locais...")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.update()

        try:
            # REMOVIDO: firebase_service.initialize_firebase() 
            # O service agora inicia o SQLite automaticamente no import

            qtd_estoque = firebase_service.get_collection_count("estoque")
            qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
            faturamento = calcular_faturamento_mes_atual()

            container_principal.content = ft.Column(
                [
                    ft.Column([
                        ft.Text("Bem-vindo de volta!", size=28, weight="bold", color=COLOR_TEXT),
                        ft.Text("Resumo da Marmoraria Central", size=15, color=ft.colors.GREY_600),
                    ]),

                    ft.Divider(height=20, color="transparent"),

                    ft.ResponsiveRow(
                        [
                            criar_card_indicador("Estoque", f"{qtd_estoque} Itens", ft.icons.INVENTORY_2_ROUNDED, COLOR_INFO),
                            criar_card_indicador("Orçamentos", f"{qtd_orcamentos}", ft.icons.DESCRIPTION_ROUNDED, COLOR_WARNING),
                            criar_card_indicador("Caixa Mensal", f"R$ {faturamento:,.2f}", ft.icons.ATTACH_MONEY_ROUNDED, COLOR_SUCCESS, COLOR_SUCCESS),
                        ],
                        spacing=20
                    ),

                    ft.Divider(height=30, color="transparent"),
                    ft.Text("Ações Rápidas", size=20, weight="bold", color=COLOR_TEXT),

                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=ft.ElevatedButton(
                                    "Novo Orçamento", icon=ft.icons.ADD_ROUNDED, height=55,
                                    bgcolor=COLOR_PRIMARY, color=COLOR_WHITE,
                                    on_click=lambda _: page.go("/orcamentos")
                                )
                            ),
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=ft.ElevatedButton(
                                    "Ver Estoque", icon=ft.icons.LIST_ALT_ROUNDED, height=55,
                                    bgcolor=COLOR_WHITE, color=COLOR_PRIMARY,
                                    on_click=lambda _: page.go("/estoque")
                                )
                            ),
                        ],
                        spacing=15
                    ),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=10
            )

        except Exception as e:
            container_principal.content = ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, color=COLOR_ERROR, size=40),
                ft.Text(f"Erro ao carregar Dashboard:\n{e}", color=COLOR_ERROR, text_align="center")
            ], horizontal_alignment="center", alignment="center")

        page.update()

    carregar_dashboard()
    return LayoutBase(page, container_principal, titulo="Dashboard")