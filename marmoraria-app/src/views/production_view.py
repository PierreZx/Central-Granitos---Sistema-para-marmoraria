import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, 
    COLOR_SECONDARY, BORDER_RADIUS_MD, COLOR_TEXT
)
from src.services import firebase_service

def ProductionView(page: ft.Page):
    # Container principal que será atualizado pelas Tabs
    conteudo_dinamico = ft.Container(expand=True, animate_opacity=300)

    def desenhar_explosao(cv_obj, item):
        """Desenha o esboço técnico da peça no Canvas"""
        cv_obj.shapes.clear()
        if not isinstance(item, dict): return

        # Dimensões do Canvas
        W = 300
        H = 150
        
        def _f(val):
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        larg = _f(item.get('largura', 0))
        prof = _f(item.get('profundidade', 0))

        if larg == 0 or prof == 0: return

        # Proporção para o desenho caber no canvas
        escala = min((W - 40) / larg, (H - 40) / prof)
        w_desenho = larg * escala
        h_desenho = prof * escala
        
        # Centralização
        x0 = (W - w_desenho) / 2
        y0 = (H - h_desenho) / 2

        # Desenho do retângulo da pedra
        cv_obj.shapes.append(
            ft.canvas.Rect(
                x0, y0, w_desenho, h_desenho, 
                border_radius=2,
                paint=ft.Paint(color=COLOR_PRIMARY, style=ft.PaintingStyle.STROKE, stroke_width=2)
            )
        )
        # Preenchimento leve
        cv_obj.shapes.append(
            ft.canvas.Rect(
                x0, y0, w_desenho, h_desenho,
                paint=ft.Paint(color=f"{COLOR_PRIMARY}10", style=ft.PaintingStyle.FILL)
            )
        )

    def abrir_visualizador(orc):
        """Abre a Ordem de Serviço detalhada"""
        itens = orc.get('itens', [])
        if not isinstance(itens, list): itens = []

        lista_pecas = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        for item in itens:
            if not isinstance(item, dict): continue

            cv_peca = ft.canvas.Canvas(width=300, height=150)
            
            lista_pecas.controls.append(
                ft.Container(
                    padding=15, 
                    bgcolor=ft.colors.GREY_50, 
                    border_radius=10,
                    border=ft.border.all(1, ft.colors.GREY_200),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(item.get('nome', 'Peça'), weight="bold", size=16),
                            ft.Container(
                                content=ft.Text(f"{item.get('largura')}x{item.get('profundidade')} cm", size=12, weight="bold"),
                                bgcolor=f"{COLOR_PRIMARY}20", padding=ft.padding.symmetric(6, 10), border_radius=5
                            )
                        ], alignment="spaceBetween"),
                        ft.Container(cv_peca, alignment=ft.alignment.center, padding=10),
                        ft.Row([
                            ft.Icon(ft.icons.ARCHITECTURE, size=16, color=ft.colors.GREY_500),
                            ft.Text(f"Acabamento: {item.get('acabamento', 'Padrão')}", size=13, color=ft.colors.GREY_700),
                        ], spacing=5)
                    ])
                )
            )
            # Chama o desenho após um pequeno delay ou garantir que o objeto existe
            desenhar_explosao(cv_peca, item)

        dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.ASSIGNMENT_SHARP, color=COLOR_PRIMARY),
                ft.Text(f"O.S. - {orc.get('cliente_nome', 'Cliente')}")
            ], spacing=10),
            content=ft.Container(content=lista_pecas, width=450, height=600),
            actions=[ft.ElevatedButton("Fechar", on_click=lambda e: page.close_dialog(), bgcolor=COLOR_PRIMARY, color=COLOR_WHITE)],
            actions_alignment="end",
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_coluna(status_firebase, titulo_coluna, cor_status):
        """Gera o grid de pedidos para cada status"""
        orcamentos = firebase_service.get_orcamentos_by_status(status_firebase)
        grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
        
        if not orcamentos:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.INBOX_ROUNDED, size=50, color=ft.colors.GREY_300),
                    ft.Text("Nenhum pedido nesta fase", color=ft.colors.GREY_500)
                ], horizontal_alignment="center"),
                padding=50, alignment=ft.alignment.center
            )

        for orc in orcamentos:
            grid.controls.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4, "xl": 3},
                    padding=20, 
                    bgcolor=COLOR_WHITE, 
                    border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=15, color="#00000008", offset=ft.Offset(0, 5)),
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(titulo_coluna.upper(), size=10, weight="bold", color=COLOR_WHITE),
                                bgcolor=cor_status, padding=ft.padding.symmetric(4, 8), border_radius=5
                            ),
                            ft.Text(f"#{orc.get('id', '')[:5]}", size=10, color=ft.colors.GREY_400)
                        ], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', 'Cliente'), weight="bold", size=18, max_lines=1, overflow="ellipsis"),
                        ft.Row([
                            ft.Icon(ft.icons.LAYERS_OUTLINED, size=16, color=ft.colors.GREY_500),
                            ft.Text(f"{len(orc.get('itens', []))} peças para produzir", size=13, color=ft.colors.GREY_600),
                        ]),
                        ft.Divider(height=20, color=ft.colors.GREY_100),
                        ft.ElevatedButton(
                            "VER DETALHES / O.S.", 
                            icon=ft.icons.REORDER_ROUNDED, 
                            bgcolor=COLOR_SECONDARY, 
                            color=COLOR_WHITE, 
                            width=float("inf"),
                            height=45,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=lambda e, o=orc: abrir_visualizador(o)
                        )
                    ], spacing=10)
                )
            )
        return grid

    def mudar_aba(e):
        idx = e.control.selected_index
        status_map = [
            ("Produção", "PENDENTE", ft.colors.ORANGE_700),
            ("Em Andamento", "PRODUZINDO", ft.colors.BLUE_700),
            ("Finalizado", "PRONTO", ft.colors.GREEN_700)
        ]
        label, tit, cor = status_map[idx]
        conteudo_dinamico.content = render_coluna(label, tit, cor)
        page.update()

    # Inicialização da primeira aba
    conteudo_dinamico.content = render_coluna("Produção", "PENDENTE", ft.colors.ORANGE_700)

    # Layout Principal com Tabs Modernas
    layout_producao = ft.Column([
        ft.Tabs(
            selected_index=0,
            label_color=COLOR_PRIMARY,
            unselected_label_color=ft.colors.GREY_500,
            indicator_color=COLOR_PRIMARY,
            indicator_border_radius=5,
            on_change=mudar_aba,
            tabs=[
                ft.Tab(text="Fila de Espera", icon=ft.icons.TIMER_OUTLINED),
                ft.Tab(text="Na Bancada", icon=ft.icons.PRECISION_MANUFACTURING),
                ft.Tab(text="Concluídos", icon=ft.icons.CHECK_CIRCLE_OUTLINE),
            ],
        ),
        ft.Container(height=10),
        conteudo_dinamico
    ], expand=True, spacing=10)

    return LayoutBase(page, layout_producao, titulo="Área de Produção", subtitulo="Gestão de Ordens de Serviço")