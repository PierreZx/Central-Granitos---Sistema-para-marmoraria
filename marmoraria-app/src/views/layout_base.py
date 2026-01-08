import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_WARNING, COLOR_TEXT
from src.services import firebase_service
from src.services import notification_service # Importa o novo serviço

def LayoutBase(page: ft.Page, conteudo_principal, titulo="Central Granitos"):
    
    # Verifica status
    conectado = firebase_service.verificar_conexao()
    pendencias = firebase_service.get_pendencias_count()
    perfil = page.session.get("user_role")
    
    # --- SISTEMA DE NOTIFICAÇÕES ---
    lista_notificacoes = notification_service.gerar_notificacoes(perfil)
    qtd_notificacoes = len(lista_notificacoes)
    
    def mostrar_notificacoes(e):
        # Cria a lista visual
        itens_view = []
        if not lista_notificacoes:
            itens_view.append(ft.Container(content=ft.Text("Nenhuma notificação nova.", color="grey"), padding=20, alignment=ft.alignment.center))
        else:
            for notif in lista_notificacoes:
                icone = ft.icons.INFO
                cor_icone = COLOR_PRIMARY
                if notif['tipo'] == 'alert': icone = ft.icons.WARNING; cor_icone = "red"
                elif notif['tipo'] == 'money': icone = ft.icons.ATTACH_MONEY; cor_icone = "green"
                elif notif['tipo'] == 'check': icone = ft.icons.CHECK_CIRCLE; cor_icone = "blue"
                elif notif['tipo'] == 'work': icone = ft.icons.BUILD; cor_icone = "orange"

                itens_view.append(ft.Container(
                    padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, "#eeeeee")),
                    content=ft.Row([
                        ft.Icon(icone, color=cor_icone),
                        ft.Column([
                            ft.Text(notif['titulo'], weight="bold", size=14),
                            ft.Text(notif['msg'], size=12, color="grey", width=200, no_wrap=False)
                        ], spacing=2)
                    ], alignment="start")
                ))

        # Drawer ou Dialog de Notificações
        bs = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Text("Notificações", weight="bold", size=20, color=COLOR_TEXT),
                    ft.Divider(),
                    ft.Column(itens_view, scroll=ft.ScrollMode.AUTO, height=300)
                ]),
                padding=20,
                bgcolor=COLOR_WHITE,
                border_radius=ft.border_radius.only(top_left=20, top_right=20)
            )
        )
        page.overlay.append(bs)
        bs.open = True
        page.update()

    # Ícone de Notificação com Badge
    icone_sino = ft.IconButton(ft.icons.NOTIFICATIONS, icon_color=COLOR_WHITE, on_click=mostrar_notificacoes)
    if qtd_notificacoes > 0:
        icone_sino = ft.Stack([
            ft.IconButton(ft.icons.NOTIFICATIONS, icon_color=COLOR_WHITE, on_click=mostrar_notificacoes),
            ft.Container(
                content=ft.Text(str(qtd_notificacoes), size=10, color=COLOR_WHITE, weight="bold"),
                bgcolor="red", border_radius=10, width=16, height=16, alignment=ft.alignment.center,
                right=5, top=5
            )
        ])

    # Ícone de Status da Rede
    icone_rede = ft.Icon(ft.icons.WIFI, color=COLOR_WHITE, size=20) if conectado else ft.Icon(ft.icons.WIFI_OFF, color=COLOR_WARNING, size=20)
    
    # Ações da AppBar
    acoes_appbar = [
        ft.Container(content=icone_rede, padding=ft.padding.only(right=10)),
        icone_sino,
        ft.Container(width=10)
    ]
    
    # Botão Sync (se houver pendencias)
    if pendencias > 0 and conectado:
        def sincronizar(e):
            page.snack_bar = ft.SnackBar(ft.Text("Sincronizando...")); page.snack_bar.open=True; page.update()
            sucesso, msg = firebase_service.sincronizar_agora()
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green" if sucesso else "red"); page.snack_bar.open=True; 
            if sucesso: page.go("/orcamentos")
            page.update()

        btn_sync = ft.Stack([
            ft.IconButton(ft.icons.SYNC, icon_color=COLOR_WHITE, on_click=sincronizar),
            ft.Container(content=ft.Text(str(pendencias), size=10, color=COLOR_WHITE), bgcolor="orange", border_radius=10, width=16, height=16, alignment=ft.alignment.center, right=5, top=5)
        ])
        acoes_appbar.insert(0, btn_sync)

    # --- MENU MOBILE ---
    sidebar_mobile = Sidebar(page, is_mobile=True)
    drawer_mobile = ft.NavigationDrawer(
        controls=[ft.Container(content=sidebar_mobile, padding=0, expand=True, bgcolor=ft.colors.WHITE)],
        bgcolor=ft.colors.WHITE,
        surface_tint_color=ft.colors.WHITE,
    )

    def show_drawer(e):
        drawer_mobile.open = True; drawer_mobile.update()

    eh_mobile = page.width < 768

    if eh_mobile:
        app_bar = ft.AppBar(
            title=ft.Row([
                ft.Image(src="logo.jpg", width=28, height=28, fit=ft.ImageFit.CONTAIN),
                ft.Text(titulo, size=16, weight=ft.FontWeight.W_600, color=COLOR_WHITE),
            ], spacing=10),
            leading=ft.IconButton(ft.icons.MENU, icon_color=COLOR_WHITE, on_click=show_drawer),
            actions=acoes_appbar, 
            bgcolor=COLOR_PRIMARY, center_title=False, elevation=0,
        )
        page.drawer = drawer_mobile
        
        barra_offline = ft.Container()
        if not conectado:
            barra_offline = ft.Container(content=ft.Text("MÓDULO OFFLINE ATIVO", size=11, color="black", weight="bold"), bgcolor=COLOR_WARNING, padding=5, alignment=ft.alignment.center, width=float('inf'))

        return ft.Container(
            content=ft.Column([
                barra_offline, 
                ft.Container(content=conteudo_principal, expand=True)
            ]),
            bgcolor=COLOR_BACKGROUND,
            expand=True
        )
        
    else:
        return ft.Row(
            [
                Sidebar(page), 
                ft.Container(content=conteudo_principal, expand=True, padding=20)
            ],
            expand=True,
            spacing=0
        )