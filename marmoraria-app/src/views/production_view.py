import flet as ft
import flet.canvas as cv
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, BORDER_RADIUS_MD
from src.services import firebase_service

def ProductionView(page: ft.Page):
    
    estado = {"aba_atual": "Pendentes"}
    conteudo = ft.Container(expand=True)

    # --- DESENHO EXPLODIDO FIT-TO-SCREEN ---
    def desenhar_explosao(cv_obj, item):
        cv_obj.shapes.clear()
        
        # Dimensões dinâmicas do canvas
        W_CANVAS = cv_obj.width if cv_obj.width else 300
        H_CANVAS = cv_obj.height if cv_obj.height else 300
        
        GAP = 30
        
        cfg = item.get('config', {})
        
        def _f(val):
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        try: 
            larg = _f(item.get('largura', 0))
            prof = _f(item.get('profundidade', 0))
        except: return

        if larg == 0 or prof == 0: return

        larg_total_virtual = larg * 1.5
        prof_total_virtual = prof * 1.5
        
        # Escala ajustada para caber bem
        scale = min((W_CANVAS - 40) / larg_total_virtual, (H_CANVAS - 40) / prof_total_virtual) * 0.60
        
        w_px, h_px = larg * scale, prof * scale
        cx, cy = W_CANVAS / 2, H_CANVAS / 2
        sx, sy = cx - (w_px / 2), cy - (h_px / 2)

        C_PEDRA, C_LINHA, C_TRACEJADO, C_RODA, C_SAIA = ft.colors.BLUE_GREY_50, ft.colors.BLACK, ft.colors.GREY_500, ft.colors.BROWN_300, ft.colors.ORANGE_300

        # BASE
        cv_obj.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=C_PEDRA)))
        cv_obj.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))
        cv_obj.shapes.append(cv.Text(sx + 5, sy + 5, f"BASE\n{larg:.2f} x {prof:.2f}m", style=ft.TextStyle(weight="bold", size=9, color=ft.colors.GREY_700)))

        # PEÇAS EXPLODIDAS
        def draw_part_exploded(k, pos, cor, nome):
            vals = cfg.get(k, {})
            if vals.get('chk'):
                comp_real = _f(vals.get('c', 0))
                alt_real = _f(vals.get('a', 0))
                if comp_real == 0: comp_real = larg if pos in ['top', 'bottom'] else prof

                THICKNESS = 15
                if pos in ['top', 'bottom']: pw, ph = comp_real * scale, THICKNESS
                else: pw, ph = THICKNESS, comp_real * scale
                
                px, py = 0, 0
                if pos == 'top':
                    px = cx - (pw / 2); py = sy - GAP - ph
                    cv_obj.shapes.append(cv.Line(px, py+ph, sx + (w_px - pw)/2, sy, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Line(px+pw, py+ph, sx + (w_px - pw)/2 + pw, sy, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Text(px + pw/2, py - 12, f"{nome}: {comp_real:.2f}x{alt_real:.2f}", alignment=ft.alignment.center, style=ft.TextStyle(size=8)))
                elif pos == 'bottom':
                    px = cx - (pw / 2); py = sy + h_px + GAP
                    cv_obj.shapes.append(cv.Line(px, py, sx + (w_px - pw)/2, sy + h_px, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Line(px+pw, py, sx + (w_px - pw)/2 + pw, sy + h_px, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Text(px + pw/2, py + ph + 3, f"{nome}: {comp_real:.2f}x{alt_real:.2f}", alignment=ft.alignment.center, style=ft.TextStyle(size=8)))
                elif pos == 'left':
                    px = sx - GAP - pw; py = cy - (ph / 2)
                    cv_obj.shapes.append(cv.Line(px+pw, py, sx, sy + (h_px - ph)/2, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Line(px+pw, py+ph, sx, sy + (h_px - ph)/2 + ph, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Text(px - 3, py + ph/2, f"{nome}\n{comp_real:.2f}x{alt_real:.2f}", alignment=ft.alignment.center_right, style=ft.TextStyle(size=8)))
                elif pos == 'right':
                    px = sx + w_px + GAP; py = cy - (ph / 2)
                    cv_obj.shapes.append(cv.Line(px, py, sx + w_px, sy + (h_px - ph)/2, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Line(px, py+ph, sx + w_px, sy + (h_px - ph)/2 + ph, paint=ft.Paint(color=C_TRACEJADO, stroke_dash_pattern=[2,2])))
                    cv_obj.shapes.append(cv.Text(px + pw + 3, py + ph/2, f"{nome}\n{comp_real:.2f}x{alt_real:.2f}", alignment=ft.alignment.center_left, style=ft.TextStyle(size=8)))

                cv_obj.shapes.append(cv.Rect(px, py, pw, ph, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=cor)))
                cv_obj.shapes.append(cv.Rect(px, py, pw, ph, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=C_LINHA)))

        draw_part_exploded('rfundo', 'top', C_RODA, "RODA"); draw_part_exploded('rfrente', 'bottom', C_RODA, "RODA")
        draw_part_exploded('resq', 'left', C_RODA, "RODA"); draw_part_exploded('rdir', 'right', C_RODA, "RODA")
        draw_part_exploded('sfundo', 'top', C_SAIA, "SAIA"); draw_part_exploded('sfrente', 'bottom', C_SAIA, "SAIA")
        draw_part_exploded('sesq', 'left', C_SAIA, "SAIA"); draw_part_exploded('sdir', 'right', C_SAIA, "SAIA")

        cuba = cfg.get('cuba', {})
        if cuba.get('chk'):
            cx = sx + (_f(cuba.get('pos', 0)) * scale)
            cw = _f(cuba.get('larg', 0)) * scale; ch = _f(cuba.get('prof', 0)) * scale
            cy = sy + (h_px - ch)/2
            cv_obj.shapes.append(cv.Rect(cx, cy, cw, ch, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="blue", stroke_dash_pattern=[2,2], stroke_width=1.5)))
            cv_obj.shapes.append(cv.Text(cx+cw/2, cy+ch/2, "CUBA", alignment=ft.alignment.center, style=ft.TextStyle(size=8, color="blue", weight="bold")))

        cook = cfg.get('cook', {})
        if cook.get('chk'):
            cx = sx + (_f(cook.get('pos', 0)) * scale)
            cw = _f(cook.get('larg', 0)) * scale; ch = _f(cook.get('prof', 0)) * scale
            cy = sy + (h_px - ch)/2
            cv_obj.shapes.append(cv.Rect(cx, cy, cw, ch, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="black", stroke_width=1.5)))
            cv_obj.shapes.append(cv.Text(cx+cw/2, cy+ch/2, "COOK", alignment=ft.alignment.center, style=ft.TextStyle(size=8, color="black", weight="bold")))

    # --- AÇÕES ---
    def abrir_dialogo_devolucao(orcamento):
        txt_motivo = ft.TextField(label="Motivo da Devolução", multiline=True)
        def confirmar_devolucao(e):
            if not txt_motivo.value: return
            firebase_service.update_orcamento(orcamento['id'], {'status': 'Retornado', 'motivo_retorno': txt_motivo.value})
            firebase_service.repor_estoque_devolucao(orcamento)
            page.close_dialog(); page.snack_bar = ft.SnackBar(ft.Text("Devolvido ao Estoque!"), bgcolor=ft.colors.ORANGE); page.snack_bar.open=True; page.update(); carregar_dados()
        
        dlg = ft.AlertDialog(title=ft.Text("Reportar Erro"), content=txt_motivo, actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()), ft.ElevatedButton("Confirmar", bgcolor=ft.colors.RED, color=COLOR_WHITE, on_click=confirmar_devolucao)])
        page.dialog = dlg; dlg.open = True; page.update()

    def abrir_visualizador(orcamento):
        lista = ft.Column(scroll=ft.ScrollMode.AUTO, height=500, spacing=15)
        lista.controls.append(ft.Container(padding=10, bgcolor=f"{COLOR_PRIMARY}10", border_radius=8, content=ft.Column([
            ft.Text(f"Cliente: {orcamento.get('cliente_nome')}", size=18, weight="bold", color=COLOR_PRIMARY),
            ft.Text(f"Contato: {orcamento.get('cliente_contato', '-')}", size=13),
            ft.Text(f"Qtd Peças: {len(orcamento.get('itens', []))}", size=13, weight="bold"),
        ])))

        # AJUSTE MOBILE: Canvas Responsivo
        eh_mobile = page.width < 768
        w_canvas_os = page.width * 0.8 if eh_mobile else 600
        h_canvas_os = 300 if eh_mobile else 500

        for i, item in enumerate(orcamento.get('itens', [])):
            cv_peca = cv.Canvas(width=w_canvas_os, height=h_canvas_os, shapes=[])
            desenhar_explosao(cv_peca, item)
            instrucoes = item.get('config', {}).get('instrucoes_producao', 'Sem observações.')
            
            lista.controls.append(ft.Container(
                bgcolor=COLOR_WHITE, padding=15, border_radius=10, border=ft.border.all(1, ft.colors.GREY_300),
                content=ft.Column([
                    ft.Text(f"Item #{i+1}: {item['ambiente']} - {item['material']}", weight="bold", size=15),
                    ft.Divider(),
                    ft.Container(content=cv_peca, alignment=ft.alignment.center, bgcolor=ft.colors.GREY_50, border_radius=10, padding=5),
                    ft.Container(height=10),
                    ft.Text("Instruções:", weight="bold", size=12, color=COLOR_PRIMARY),
                    ft.Container(padding=10, bgcolor=ft.colors.YELLOW_50, border_radius=5, width=float('inf'), content=ft.Text(instrucoes, size=13, color=ft.colors.BLACK87))
                ])
            ))

        botoes = []
        status = orcamento.get('status')
        if status != "Finalizado": botoes.append(ft.ElevatedButton("Reportar Erro", icon=ft.icons.WARNING, bgcolor=ft.colors.RED, color=COLOR_WHITE, on_click=lambda e: abrir_dialogo_devolucao(orcamento)))
        if status in ["Produção", "Em Aberto"]: botoes.append(ft.ElevatedButton("Iniciar", icon=ft.icons.PLAY_ARROW, bgcolor=ft.colors.BLUE, color=COLOR_WHITE, on_click=lambda e: atualizar_status(orcamento, "Em Andamento")))
        if status == "Em Andamento": botoes.append(ft.ElevatedButton("Finalizar", icon=ft.icons.CHECK_CIRCLE, bgcolor=ft.colors.GREEN, color=COLOR_WHITE, on_click=lambda e: atualizar_status(orcamento, "Finalizado")))

        # CORREÇÃO: Width do Dialog dinâmico (90% da tela se mobile)
        dlg_width = page.width * 0.9 if eh_mobile else 800

        dlg = ft.AlertDialog(
            title=ft.Text("Ordem de Serviço", weight="bold"), 
            content=ft.Container(width=dlg_width, content=lista), # Width centralizado
            actions=[ft.TextButton("Fechar", on_click=lambda e: page.close_dialog()), *botoes], 
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg; dlg.open = True; page.update()

    def atualizar_status(orc, novo):
        firebase_service.update_orcamento(orc['id'], {'status': novo})
        page.close_dialog(); carregar_dados()

    def render_coluna(status_filtro, titulo, cor_badge):
        lista = firebase_service.get_orcamentos_lista()
        filtrados = [o for o in lista if o.get('status') == status_filtro]
        
        # Grid com apenas 1 coluna se for mobile para centralizar os cards
        eh_mobile = page.width < 768
        cols = 1 if eh_mobile else 3
        
        grid = ft.GridView(expand=True, runs_count=cols, max_extent=400, spacing=15, run_spacing=15, child_aspect_ratio=1.0)
        
        if not filtrados: grid.controls.append(ft.Container(content=ft.Text("Nenhum item.", color="grey"), alignment=ft.alignment.center, padding=40))
        else:
            for orc in filtrados:
                grid.controls.append(ft.Container(
                    bgcolor=COLOR_WHITE, border_radius=15, padding=15, shadow=ft.BoxShadow(blur_radius=5, color="#00000010"),
                    content=ft.Column([
                        ft.Row([ft.Container(content=ft.Text(status_filtro, size=10, color=COLOR_WHITE, weight="bold"), bgcolor=cor_badge, padding=5, border_radius=5), ft.Icon(ft.icons.BUILD_CIRCLE, color=COLOR_PRIMARY)], alignment="spaceBetween"),
                        ft.Text(orc.get('cliente_nome', ''), weight="bold", size=16, color=ft.colors.BLACK87),
                        ft.Text(f"{len(orc.get('itens', []))} peças", size=13, color="grey"),
                        ft.Divider(),
                        ft.ElevatedButton("Abrir O.S.", icon=ft.icons.VISIBILITY, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, width=float("inf"), on_click=lambda e, o=orc: abrir_visualizador(o))
                    ])
                ))
        return grid

    def carregar_dados():
        tabs = ft.Tabs(selected_index=0, animation_duration=300, label_color=COLOR_PRIMARY, indicator_color=COLOR_PRIMARY, tabs=[
            ft.Tab(text="Pendentes", content=ft.Container(padding=10, content=render_coluna("Produção", "A Fazer", ft.colors.ORANGE))),
            ft.Tab(text="Andamento", content=ft.Container(padding=10, content=render_coluna("Em Andamento", "Produzindo", ft.colors.BLUE))),
            ft.Tab(text="Finalizados", content=ft.Container(padding=10, content=render_coluna("Finalizado", "Pronto", ft.colors.GREEN))),
        ], expand=True)
        conteudo.content = ft.Container(padding=10, expand=True, content=ft.Column([ft.Text("Produção", size=24, weight="bold", color=COLOR_PRIMARY), ft.Divider(), tabs]))
        page.update()

    carregar_dados()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Produção")