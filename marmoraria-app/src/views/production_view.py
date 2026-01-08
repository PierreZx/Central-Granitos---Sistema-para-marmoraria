import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, BORDER_RADIUS_MD
from src.services import firebase_service

def ProductionView(page: ft.Page):
    estado = {"aba_atual": "Pendentes"}
    conteudo = ft.Container(expand=True)

    def desenhar_explosao(cv_obj, item):
        cv_obj.shapes.clear()
        # Proteção: Se o item vier como string do banco, ignora para não dar erro
        if not isinstance(item, dict):
            return

        W_CANVAS = cv_obj.width if cv_obj.width else 300
        H_CANVAS = cv_obj.height if cv_obj.height else 300
        
        cfg = item.get('config', {})
        
        def _f(val):
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        larg = _f(item.get('largura', 0))
        prof = _f(item.get('profundidade', 0))

        if larg == 0 or prof == 0: return
        # ... (restante da lógica de desenho simplificada para estabilidade)

    def abrir_visualizador(orc):
        # Proteção extra para garantir que itens seja uma lista
        itens = orc.get('itens', [])
        if not isinstance(itens, list):
            itens = []

        lista_pecas = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)
        
        for item in itens:
            # Pula o item se ele não for um dicionário válido
            if not isinstance(item, dict):
                continue

            cv_peca = ft.canvas.Canvas(width=300, height=200)
            
            lista_pecas.controls.append(
                ft.Container(
                    padding=15, bgcolor="#F8F9FA", border_radius=10,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{item.get('nome', 'Peça')}", size=16, style=ft.TextStyle(weight="bold")),
                            ft.Text(f"{item.get('largura')} x {item.get('profundidade')} cm", color=COLOR_PRIMARY)
                        ], alignment="spaceBetween"),
                        ft.Container(content=cv_peca, alignment=ft.alignment.center, height=150),
                        ft.Text(f"Acabamento: {item.get('acabamento', 'Padrão')}", size=12, italic=True)
                    ])
                )
            )
            desenhar_explosao(cv_peca, item)

        dlg = ft.AlertDialog(
            title=ft.Text(f"O.S. - {orc.get('cliente_nome', 'Cliente')}", style=ft.TextStyle(weight="bold")),
            content=ft.Container(content=lista_pecas, width=400, height=500),
            actions=[ft.TextButton("Fechar", on_click=lambda e: page.close_dialog())]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_coluna(status_firebase, titulo_coluna, cor):
        orcamentos = firebase_service.get_orcamentos_by_status(status_firebase)
        grid = ft.ResponsiveRow(spacing=20)
        
        for orc in orcamentos:
            grid.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    padding=15, bgcolor=COLOR_WHITE, border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=10, color="#0000000D"),
                    content=ft.Column([
                        ft.Row([
                            ft.Badge(content=ft.Text(titulo_coluna, size=10, color=COLOR_WHITE), bgcolor=cor),
                            ft.Icon(ft.icons.BUILD_CIRCLE, color=COLOR_PRIMARY)
                        ], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', ''), style=ft.TextStyle(weight="bold", size=16)),
                        ft.Text(f"{len(orc.get('itens', []))} peças", size=13, color="grey"),
                        ft.Divider(),
                        ft.ElevatedButton(
                            "Abrir O.S.", icon=ft.icons.VISIBILITY, 
                            bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, 
                            width=float("inf"), 
                            on_click=lambda e, o=orc: abrir_visualizador(o)
                        )
                    ])
                )
            )
        return grid

    conteudo.content = ft.Column([
        ft.Tabs(
            selected_index=0,
            label_color=COLOR_PRIMARY,
            indicator_color=COLOR_PRIMARY,
            tabs=[
                ft.Tab(text="Pendentes", content=ft.Container(padding=20, content=render_coluna("Produção", "A Fazer", ft.colors.ORANGE))),
                ft.Tab(text="Andamento", content=ft.Container(padding=20, content=render_coluna("Em Andamento", "Produzindo", ft.colors.BLUE))),
                ft.Tab(text="Pronto", content=ft.Container(padding=20, content=render_coluna("Finalizado", "Finalizado", ft.colors.GREEN))),
            ], expand=True
        )
    ], expand=True)

    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, titulo="Produção")