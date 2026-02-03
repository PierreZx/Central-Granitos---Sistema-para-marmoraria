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

    # Container principal que recebe o conteúdo dinâmico
    container_principal = ft.Container(expand=True)

    # ======================================================
    # ===================== CARD KPI =======================
    # ======================================================
    def criar_card_indicador(titulo, valor, icone, cor):
        return ft.Container(
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
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.Container(
                        width=54,
                        height=54,
                        bgcolor=f"{cor}15",
                        border_radius=12,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            name=icone,
                            color=cor,
                            size=28,
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                titulo,
                                size=13,
                                color="grey600",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                valor,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                            ),
                        ],
                    ),
                ],
            ),
        )

    # ======================================================
    # ================== CARREGAMENTO ======================
    # ======================================================
    def carregar_dashboard(e=None):
        # Estado de loading
        container_principal.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(color=COLOR_PRIMARY),
                ft.Text(
                    " Sincronizando dados da Central...",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        )
        page.update()

        try:
            # Inicialização Firebase
            firebase_service.initialize_firebase()

            qtd_estoque = firebase_service.get_collection_count("estoque")
            qtd_orcamentos = firebase_service.get_collection_count("orcamentos")

            try:
                extrato = firebase_service.get_extrato_lista()
                faturamento = sum(
                    float(item.get("valor", 0))
                    for item in extrato
                    if item.get("tipo") == "Entrada"
                )
            except Exception:
                faturamento = 0.0

            # Conteúdo principal
            container_principal.content = ft.Column(
                expand=True,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
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
                        ],
                    ),

                    ft.Divider(height=30, color="transparent"),

                    # KPIs
                    ft.ResponsiveRow(
                        spacing=20,
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
                        spacing=15,
                        controls=[
                            ft.Container(
                                col={"xs": 12, "sm": 6, "md": 3},
                                content=ft.ElevatedButton(
                                    text="Novo Orçamento",
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
                                    text="Consultar Estoque",
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
                    ),
                ],
            )

        except Exception as err:
            # Tela de erro
            container_principal.content = ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            name="error_outline",
                            color=COLOR_ERROR,
                            size=50,
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
                            text="Tentar novamente",
                            on_click=carregar_dashboard,
                        ),
                    ],
                ),
            )

        page.update()

    # ======================================================
    # CARREGAMENTO INICIAL
    # ======================================================
    carregar_dashboard()

    # ======================================================
    # RETORNO COM LAYOUT BASE (ASSINATURA ORIGINAL)
    # ======================================================
    return LayoutBase(
        page,
        container_principal,
        titulo="Dashboard",
    )
