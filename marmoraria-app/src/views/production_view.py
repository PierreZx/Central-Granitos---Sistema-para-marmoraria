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
        cv_obj.shapes.clear()
        pecas = item.get('pecas', {})
        furos = item.get('furos', {}) # Pegando os furos salvos
        if not pecas: return

        # 1. Medidas e Escala
        w1 = float(pecas.get('p1', {}).get('l', 0))
        h1 = float(pecas.get('p1', {}).get('p', 0))
        w2 = float(pecas.get('p2', {}).get('l', 0)) if 'p2' in pecas else 0
        w3 = float(pecas.get('p3', {}).get('l', 0)) if 'p3' in pecas else 0
        
        total_w = w1 + w2 + w3
        max_h = max(h1, 
                    float(pecas.get('p2', {}).get('p', 0)) if 'p2' in pecas else 0,
                    float(pecas.get('p3', {}).get('p', 0)) if 'p3' in pecas else 0)

        W_CANVAS, H_CANVAS = 300, 150
        scale = min((W_CANVAS - 60) / max(0.1, total_w), (H_CANVAS - 40) / max(0.1, max_h))

        # Centralização base
        start_x = (W_CANVAS - (total_w * scale)) / 2
        p1_y = (H_CANVAS - (h1 * scale)) / 2

        def draw_rect(w, h, x, y, nome, is_p1=False):
            wp, hp = w * scale, h * scale
            # Desenha a pedra
            cv_obj.shapes.append(ft.canvas.Rect(x, y, wp, hp, border_radius=2,
                paint=ft.Paint(color=COLOR_PRIMARY, style=ft.PaintingStyle.STROKE, stroke_width=2)))
            
            # Se for P1 e tiver furos, desenha os furos dentro dela
            if is_p1:
                if furos.get('bojo', {}).get('check'):
                    # Desenha um círculo/retalho simbólico do bojo centralizado na P1
                    cv_obj.shapes.append(ft.canvas.Rect(x + (wp*0.3), y + (hp*0.2), wp*0.4, hp*0.6, border_radius=10,
                        paint=ft.Paint(color=ft.colors.RED_400, style=ft.PaintingStyle.STROKE, stroke_width=1)))
                    cv_obj.shapes.append(ft.canvas.Text(x + (wp*0.35), y + (hp*0.4), "BOJO", style=ft.TextStyle(size=8, color=ft.colors.RED_400)))
                
                if furos.get('cooktop', {}).get('check'):
                    # Desenha um retângulo do cooktop
                    cv_obj.shapes.append(ft.canvas.Rect(x + (wp*0.6), y + (hp*0.2), wp*0.3, hp*0.5,
                        paint=ft.Paint(color=ft.colors.BLUE_400, style=ft.PaintingStyle.STROKE, stroke_width=1)))
                    cv_obj.shapes.append(ft.canvas.Text(x + (wp*0.62), y + (hp*0.4), "COOK", style=ft.TextStyle(size=7, color=ft.colors.BLUE_400)))

            # Texto da medida
            cv_obj.shapes.append(ft.canvas.Text(x + 2, y - 15, f"{nome}: {w}x{h}", 
                style=ft.TextStyle(size=9, weight="bold", color=COLOR_TEXT)))

        # Lógica de empilhamento horizontal (P2 esquerda -> P1 -> P3 direita)
        curr_x = start_x
        # P2 (se for esquerda)
        if 'p2' in pecas and pecas['p2'].get('lado') == 'esquerda':
            draw_rect(w2, float(pecas['p2']['p']), curr_x, p1_y, "P2")
            curr_x += w2 * scale
        
        # P1 (Sempre no meio ou início)
        p1_x = curr_x
        draw_rect(w1, h1, p1_x, p1_y, "P1", is_p1=True)
        curr_x += w1 * scale

        # P2 ou P3 (se forem direita)
        for p_key in ['p2', 'p3']:
            if p_key in pecas and pecas[p_key].get('lado') == 'direita':
                draw_rect(float(pecas[p_key]['l']), float(pecas[p_key]['p']), curr_x, p1_y, p_key.upper())
                curr_x += float(pecas[p_key]['l']) * scale

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