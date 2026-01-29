import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_BACKGROUND,
    COLOR_WHITE,
    COLOR_WARNING,
    COLOR_TEXT
)
from src.services import firebase_service


def LayoutBase(
    page: ft.Page,
    conteudo_principal,
    titulo="Central Granitos",
    subtitulo=None
):
    """
    Layout base unificado
    Totalmente compatível com Flet 0.23.2
    """

    # ------------------------------------------------------
    # ---------------- STATUS DE CONEXÃO -------------------
    # ------------------------------------------------------

    conectado = firebase_service.verificar_conexao()

    # ------------------------------------------------------
    # ---------------- DETECÇÃO DE MOBILE ------------------
    # ------------------------------------------------------

    eh_mobile = page.width < 768

    # ------------------------------------------------------
    # ---------------- DRAWER (MOBILE) ---------------------
    # ------------------------------------------------------

    drawer_mobile = ft.Container(
        content=Sidebar(page, is_mobile=True),
        width=260,
        bgcolor=COLOR_WHITE,
        padding=0
    )

    def abrir_menu(e):
        page.drawer = drawer_mobile
        page.drawer.open = True
        page.update()

    # ------------------------------------------------------
    # ---------------- CONTEÚDO PRINCIPAL ------------------
    # ------------------------------------------------------

    view_wrapper = ft.Container(
        content=conteudo_principal,
        padding=20 if eh_mobile else 30,
        expand=True
    )

    # ======================================================
    # ======================== MOBILE ======================
    # ======================================================

    if eh_mobile:

        app_bar = ft.AppBar(
            leading=ft.IconButton(
                icon="menu",
                icon_color=COLOR_WHITE,
                on_click=abrir_menu
            ),
            title=ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_WHITE
                    ),
                    ft.Text(
                        subtitulo,
                        size=11,
                        color=COLOR_WHITE
                    ) if subtitulo else ft.Container()
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            center_title=True,
            bgcolor=COLOR_PRIMARY,
            elevation=0
        )

        barra_status = ft.Container()
        if not conectado:
            barra_status = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            "wifi_off",
                            size=14,
                            color="black87"
                        ),
                        ft.Text(
                            "OFFLINE",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color="black87"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6
                ),
                bgcolor=COLOR_WARNING,
                padding=8,
                width=float("inf")
            )

        # page.appbar e page.drawer são aplicados no main.py
        return ft.Container(
            content=ft.Column(
                controls=[
                    barra_status,
                    view_wrapper
                ],
                spacing=0
            ),
            expand=True,
            bgcolor=COLOR_BACKGROUND,
            data={
                "appbar": app_bar,
                "drawer": drawer_mobile
            }
        )

    # ======================================================
    # ======================= DESKTOP ======================
    # ======================================================

    return ft.Container(
        content=ft.Row(
            controls=[
                Sidebar(page, is_mobile=False),
                ft.Column(
                    controls=[view_wrapper],
                    expand=True,
                    spacing=0
                )
            ],
            expand=True,
            spacing=0
        ),
        expand=True,
        bgcolor=COLOR_BACKGROUND
    )
