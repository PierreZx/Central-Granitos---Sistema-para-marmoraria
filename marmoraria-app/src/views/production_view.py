# src/views/production_view.py
import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, 
    COLOR_SECONDARY, BORDER_RADIUS_MD, COLOR_TEXT
)
from src.services import firebase_service

def ProductionView(page: ft.Page):
    # Container dinâmico com animação para troca de abas
    conteudo_dinamico = ft.Container(expand=True, animate_opacity=300)

    def desenhar_explosao(cv_obj, item):
        """Renderiza o desenho técnico adaptado para a largura do telemóvel."""
        cv_obj.shapes.clear()
        pecas = item.get('pecas', {})
        if not pecas: return

        # Cálculo de Escala para Mobile
        largura_disponivel = page.width - 100 # Margem de segurança
        w1 = float(pecas.get('p1', {}).get('l', 0))
        w2 = float(pecas.get('p2', {}).get('l', 0)) if 'p2' in pecas else 0
        w3 = float(pecas.get('p3', {}).get('l', 0)) if 'p3' in pecas else 0
        total_real = w1 + w2 + w3
        
        # Define a escala baseada na largura da tela
        escala = (largura_disponivel / total_real) if total_real > 0 else 1
        if escala > 100: escala = 80 # Limite para peças pequenas não ficarem gigantes

        def draw_rect(x, y, w, h, label):
            # Desenha a pedra
            cv_obj.shapes.append(ft.cv.Rect(x, y, w * escala, h * escala, 5, 
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=COLOR_PRIMARY, stroke_width=2)))
            # Texto da medida
            cv_obj.shapes.append(ft.cv.Text(x + 5, y + 15, f"{label} ({w}x{h})", 
                ft.TextStyle(size=10, color=COLOR_TEXT, weight="bold")))

        # Renderização sequencial das peças
        curr_x = 10
        for p_key in ['p1', 'p2', 'p3']:
            if p_key in pecas:
                p = pecas[p_key]
                draw_rect(curr_x, 30, float(p['l']), float(p['p']), p_key.upper())
                curr_x += float(p['l']) * escala + 10

    def atualizar_status(item, novo_status):
        item["status"] = novo_status
        firebase_service.update_document("orcamentos", item["id"], item)
        # Recarrega a aba atual
        status_atual = "PENDENTE" if novo_status == "PRODUZINDO" else "PRODUZINDO"
        # Simplificação para o APK: recarrega a vista
        page.go("/producao")

    def render_coluna(titulo, status_filtro, cor_tema):
        orcamentos = firebase_service.get_collection("orcamentos")
        # Filtra pela coleção local
        itens_producao = []
        for o in orcamentos:
            if o.get("status") == status_filtro:
                for idx, item in enumerate(o.get("itens", [])):
                    item_copy = item.copy()
                    item_copy["id"] = o["id"] # Vincula ao ID do orçamento para update
                    item_copy["cliente"] = o.get("cliente_nome", "Cliente")
                    itens_producao.append(item_copy)

        if not itens_producao:
            return ft.Column([
                ft.Container(height=50),
                ft.Icon(ft.icons.FACT_CHECK_OUTLINED, size=50, color="grey300"),
                ft.Text(f"Sem itens em {titulo.lower()}", color="grey400")
            ], horizontal_alignment="center", width=float("inf"))

        grid = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        for item in itens_producao:
            canvas = ft.cv.Canvas(height=150, expand=True)
            desenhar_explosao(canvas, item)
            
            # Botão de ação baseado no status
            btn_acao = ft.ElevatedButton(
                "Iniciar" if status_filtro == "PENDENTE" else "Finalizar",
                bgcolor=cor_tema, color=COLOR_WHITE,
                on_click=lambda _, i=item: atualizar_status(i, "PRODUZINDO" if status_filtro == "PENDENTE" else "PRONTO")
            )

            grid.controls.append(
                ft.Container(
                    padding=15, bgcolor=COLOR_WHITE, border_radius=12, shadow=ft.BoxShadow(blur_radius=5, color="grey200"),
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.PERSON, size=16, color=COLOR_PRIMARY),
                            ft.Text(item['cliente'], weight="bold", size=14),
                            ft.Container(expand=True),
                            ft.Text(item.get('ambiente', 'Geral').upper(), size=11, weight="bold", color="grey600")
                        ]),
                        ft.Text(f"Material: {item.get('material', 'Granito')}", size=13),
                        ft.Divider(height=10, color="transparent"),
                        ft.Container(content=canvas, padding=5, border=ft.border.all(1, "grey100"), border_radius=8),
                        ft.Row([btn_acao], alignment="end")
                    ])
                )
            )
        return grid

    def mudar_aba(e):
        idx = e.control.selected_index
        if idx == 0:
            conteudo_dinamico.content = render_coluna("Fila de Espera", "PENDENTE", ft.colors.ORANGE_800)
        elif idx == 1:
            conteudo_dinamico.content = render_coluna("Na Bancada", "PRODUZINDO", ft.colors.BLUE_800)
        else:
            conteudo_dinamico.content = render_coluna("Finalizado", "PRONTO", ft.colors.GREEN_800)
        page.update()

    # Inicializa na primeira aba
    conteudo_dinamico.content = render_coluna("Fila de Espera", "PENDENTE", ft.colors.ORANGE_800)

    layout_final = ft.Column([
        ft.Tabs(
            selected_index=0,
            on_change=mudar_aba,
            tabs=[
                ft.Tab(text="FILA", icon=ft.icons.STAIRS_OUTLINED),
                ft.Tab(text="BANCADA", icon=ft.icons.PRECISION_MANUFACTURING),
                ft.Tab(text="PRONTO", icon=ft.icons.DONE_ALL),
            ],
        ),
        ft.Divider(height=1, color="grey200"),
        conteudo_dinamico
    ], expand=True)

    return LayoutBase(page, layout_final, titulo="Produção Ativa")