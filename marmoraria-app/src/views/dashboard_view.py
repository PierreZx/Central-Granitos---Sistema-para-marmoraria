import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_BACKGROUND,
    COLOR_WHITE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_INFO,
    COLOR_TEXT,
    COLOR_ERROR,
)
from src.services import firebase_service


def DashboardView(page: ft.Page):

    container_principal = ft.Container(expand=True)

    # ======================================================
    # ===================== CARD KPI =======================
    # ======================================================

    def criar_card_indicador(titulo, valor, icone, cor):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=54,
                        height=54,
                        bgcolor=f"{cor}15",
                        border_radius=12,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            icone,
                            color=cor,
                            size=28
                        ),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                titulo,
                                size=13,
                                color="grey600",
                                weight="bold",
                            ),
                            ft.Text(
                                valor,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=15,
            ),
            col={"xs": 12, "sm": 6, "lg": 4},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=-5,
                color="black12",
                offset=ft.Offset(0, 8),
            ),
        )

    # ======================================================
    # ================== CARREGAMENTO ======================
    # ======================================================

    def carregar_dashboard(e=None):

        container_principal.content = ft.Row(
            controls=[
                ft.ProgressRing(color=COLOR_PRIMARY),
                ft.Text(
                    " Sincronizando dados da Central...",
                    size=16,
                    weight="bold",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        page.update()

        try:
            firebase_service.initialize_firebase()

            qtd_estoque = firebase_service.get_collection_count("estoque")
            qtd_orcamentos = firebase_service.get_collection_count("orcamentos")

            try:
                extrato = firebase_service.get_extrato_lista()
                faturamento = sum(
                    float(m.get("valor", 0))
                    for m in extrato
                    if m.get("tipo") == "Entrada"
                )
            except Exception:
                faturamento = 0.0

            container_principal.content = ft.Column(
                controls=[
                    # Cabeçalho
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Bem-vindo de volta!",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                            ),
                            ft.Text(
                                "Resumo da Central Granitos hoje.",
                                size=15,
                                color="grey600",
                            ),
                        ]
                    ),

                    ft.Divider(height=30, color="transparent"),

                    # KPIs
                    ft.ResponsiveRow(
                        controls=[
                            criar_card_indicador(
                                "Estoque Total",
                                f"{qtd_estoque} Chapas",
                                "inventory",
                                COLOR_INFO,
                            ),
                            criar_card_indicador(
                                "Orçamentos Ativos",
                                f"{qtd_orcamentos}",
                                "description",
                                COLOR_WARNING,
                            ),
                            criar_card_indicador(
                                "Faturamento",
                                f"R$ {faturamento:,.2f}",
                                "attach_money",
                                COLOR_SUCCESS,
                            ),
                        ],
                        spacing=20,
                    ),

                    ft.Divider(height=40, color="transparent"),

                    # Ações rápidas
                    ft.Text(
                        "Ações Rápidas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT,
                    ),

                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                col={"xs": 12, "sm": 6, "md": 3},
                                content=ft.ElevatedButton(
                                    "Novo Orçamento",
                                    icon="add",
                                    height=55,
                                    bgcolor=COLOR_PRIMARY,
                                    color=COLOR_WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12)
                                    ),
                                    on_click=lambda e: page.go("/orcamentos"),
                                ),
                            ),
                            ft.Container(
                                col={"xs": 12, "sm": 6, "md": 3},
                                content=ft.ElevatedButton(
                                    "Consultar Estoque",
                                    icon="list_alt",
                                    height=55,
                                    bgcolor=COLOR_WHITE,
                                    color=COLOR_PRIMARY,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12)
                                    ),
                                    on_click=lambda e: page.go("/estoque"),
                                ),
                            ),
                        ],
                        spacing=15,
                    ),
                ],
                expand=True,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )

        except Exception as err:
            container_principal.content = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            "error_outline",
                            color=COLOR_ERROR,
                            size=50
                        ),
                        ft.Text(
                            "Erro ao carregar Dashboard",
                            color=COLOR_ERROR,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            str(err),
                            size=12,
                            color="grey600",
                        ),
                        ft.ElevatedButton(
                            "Tentar novamente",
                            on_click=carregar_dashboard,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )

        page.update()

    # Carregamento inicial
    carregar_dashboard()

    return LayoutBase(
        page,
        container_principal,
        titulo="Dashboard"
    )
