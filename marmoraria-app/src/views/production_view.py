import flet as ft
import flet.canvas as cv
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY
from src.services import firebase_service

def ProductionView(page: ft.Page):
    
    estado = {"aba_atual": "Pendentes"}
    conteudo = ft.Container(expand=True)

    # --- DESENHO EXPLODIDO ---
    def desenhar_explosao(cv_obj, item):
        cv_obj.shapes.clear()
        W, H, GAP = 500, 400, 30
        cfg = item.get('config', {})
        try: larg = float(item.get('largura', 0)); prof = float(item.get('profundidade', 0))
        except: return
        if larg == 0 or prof == 0: return

        larg_total_est, prof_total_est = larg * 1.4, prof * 1.4
        scale = min((W - 60) / larg_total_est, (H - 60) / prof_total_est) * 0.8
        w_px, h_px = larg * scale, prof * scale
        cx, cy = W/2, H/2
        sx, sy = cx - (w_px / 2), cy - (h_px / 2)

        COR_TAMPO, COR_PECA, COR_LINHA, COR_COTA = ft.colors.BLUE_GREY_100, ft.colors.BLUE_GREY_200, ft.colors.BLACK, ft.colors.RED_900 
        
        cv_obj.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=COR_TAMPO)))
        cv_obj.shapes.append(cv.Rect(sx, sy, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2, color=COR_LINHA)))
        cv_obj.shapes.append(cv.Text(cx, cy, f"{larg:.2f} x {prof:.2f}", alignment=ft.alignment.center, style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD)))

        def draw_part(pos, tipo, medida):
            if medida <= 0: return
            e_vis = 15
            px, py, pw, ph, lbl = 0, 0, 0, 0, f"{tipo}: {medida:.2f}"
            
            if pos == 'top': pw, ph, px, py = w_px, e_vis, sx, sy - e_vis - GAP; cv_obj.shapes.append(cv.Line(sx+w_px/2, sy, sx+w_px/2, py+ph, paint=ft.Paint(color="grey", stroke_dash_pattern=[4,4])))
            elif pos == 'bottom': pw, ph, px, py = w_px, e_vis, sx, sy + h_px + GAP; cv_obj.shapes.append(cv.Line(sx+w_px/2, sy+h_px, sx+w_px/2, py, paint=ft.Paint(color="grey", stroke_dash_pattern=[4,4])))
            elif pos == 'left': pw, ph, px, py, lbl = e_vis, h_px, sx - e_vis - GAP, sy, f"{medida:.2f}"; cv_obj.shapes.append(cv.Line(sx, sy+h_px/2, px+pw, sy+h_px/2, paint=ft.Paint(color="grey", stroke_dash_pattern=[4,4])))
            elif pos == 'right': pw, ph, px, py, lbl = e_vis, h_px, sx + w_px + GAP, sy, f"{medida:.2f}"; cv_obj.shapes.append(cv.Line(sx+w_px, sy+h_px/2, px, sy+h_px/2, paint=ft.Paint(color="grey", stroke_dash_pattern=[4,4])))

            cv_obj.shapes.append(cv.Rect(px, py, pw, ph, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=COR_PECA)))
            cv_obj.shapes.append(cv.Rect(px, py, pw, ph, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=COR_LINHA)))
            
            tx, ty = (px + pw/2 - 20, py - 15) if pos == 'top' else (px + pw/2 - 20, py + 25) if pos == 'bottom' else (px - 25, py + ph/2 - 5) if pos == 'left' else (px + 35, py + ph/2 - 5)
            cv_obj.shapes.append(cv.Text(tx, ty, lbl, style=ft.TextStyle(size=10, color=COR_COTA, weight=ft.FontWeight.BOLD)))

        vals = cfg.get('rfundo', {}); 
        if vals.get('chk'): draw_part('top', 'Roda', float(vals.get('a', 0)))
        vals = cfg.get('rfrente', {}); 
        if vals.get('chk'): draw_part('bottom', 'Roda', float(vals.get('a', 0)))
        vals = cfg.get('resq', {}); 
        if vals.get('chk'): draw_part('left', 'Roda', float(vals.get('a', 0)))
        vals = cfg.get('rdir', {}); 
        if vals.get('chk'): draw_part('right', 'Roda', float(vals.get('a', 0)))
        vals = cfg.get('sfrente', {}); 
        if vals.get('chk'): draw_part('bottom', 'Saia', float(vals.get('a', 0)))

        cuba = cfg.get('cuba', {})
        if cuba.get('chk'):
            dist = float(cuba.get('pos', 0)) * scale
            cw, ch = w_px * 0.4, h_px * 0.6
            cx, cy = sx + dist, sy + (h_px - ch)/2 
            cv_obj.shapes.append(cv.Rect(cx, cy, cw, ch, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.RED, stroke_dash_pattern=[5,5])))
            cv_obj.shapes.append(cv.Text(cx, cy - 10, "CORTE", style=ft.TextStyle(size=10, color="red")))

    # --- AÇÃO DE DEVOLUÇÃO (COM ESTORNO DE ESTOQUE) ---
    def abrir_dialogo_devolucao(orcamento):
        txt_motivo = ft.TextField(label="Motivo da Devolução (Obrigatório)", multiline=True, min_lines=3)
        
        def confirmar_devolucao(e):
            if not txt_motivo.value:
                txt_motivo.error_text = "Descreva o erro."
                txt_motivo.update()
                return
            
            # 1. Atualiza status no banco
            firebase_service.update_orcamento(orcamento['id'], {
                'status': 'Retornado',
                'motivo_retorno': txt_motivo.value
            })
            
            # 2. DEVOLVE PEDRA PRO ESTOQUE (Estorno)
            try:
                ok_est, msg_est = firebase_service.repor_estoque_devolucao(orcamento)
                msg_final = "Devolvido! Estoque estornado." if ok_est else f"Devolvido, mas erro estoque: {msg_est}"
            except Exception as ex:
                msg_final = f"Devolvido. Erro crítico estorno: {ex}"

            page.close_dialog()
            page.snack_bar = ft.SnackBar(ft.Text(msg_final), bgcolor=ft.colors.ORANGE)
            page.snack_bar.open = True
            page.update()
            carregar_dados()

        dlg_dev = ft.AlertDialog(
            title=ft.Text("Devolver / Reportar"),
            content=ft.Column([
                ft.Text("Motivo (Isso devolverá o material ao estoque):"),
                txt_motivo
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close_dialog()),
                ft.ElevatedButton("Confirmar", bgcolor=ft.colors.RED, color=COLOR_WHITE, on_click=confirmar_devolucao)
            ]
        )
        page.dialog = dlg_dev
        dlg_dev.open = True
        page.update()

    def abrir_visualizador(orcamento):
        lista = ft.Column(scroll=ft.ScrollMode.AUTO, height=500, spacing=30)
        itens = orcamento.get('itens', [])
        if not itens: lista.controls.append(ft.Text("Vazio."))
        
        def ler_instrucoes_peca(e, texto_instrucao, titulo_peca):
            dlg_texto = ft.AlertDialog(title=ft.Text(f"Instruções: {titulo_peca}"), content=ft.Container(content=ft.Text(texto_instrucao if texto_instrucao else "Nenhuma instrução.", size=16), width=500, padding=10), actions=[ft.TextButton("Fechar", on_click=lambda e: fechar_dlg(dlg_texto))])
            page.dialog = dlg_texto; dlg_texto.open = True; page.update()

        def fechar_dlg(dlg): dlg.open = False; page.update()

        for i, item in enumerate(itens):
            cv_peca = cv.Canvas(width=500, height=400, shapes=[])
            desenhar_explosao(cv_peca, item)
            instrucoes = item.get('config', {}).get('instrucoes_producao', '')
            titulo = f"Peça {i+1}: {item['ambiente']}"

            lista.controls.append(ft.Container(
                bgcolor=ft.colors.WHITE, padding=20, border_radius=10, border=ft.border.all(1, ft.colors.GREY_300),
                content=ft.Column([
                    ft.Row([
                        ft.Text(titulo, weight="bold", size=16),
                        ft.ElevatedButton("📋 Instruções", bgcolor=ft.colors.BLUE_GREY_50, color=ft.colors.BLUE_GREY_900, on_click=lambda e, t=instrucoes, ti=titulo: ler_instrucoes_peca(e, t, ti))
                    ], alignment="spaceBetween"),
                    ft.Divider(),
                    ft.Container(content=cv_peca, alignment=ft.alignment.center, bgcolor=ft.colors.GREY_50, border_radius=10)
                ])
            ))

        botoes = []
        status = orcamento.get('status')
        if status != "Finalizado": botoes.append(ft.ElevatedButton("Devolver / Erro", icon=ft.icons.WARNING, bgcolor=ft.colors.RED, color=COLOR_WHITE, on_click=lambda e: abrir_dialogo_devolucao(orcamento)))
        if status in ["Produção", "Em Aberto"]: botoes.append(ft.ElevatedButton("Iniciar", icon=ft.icons.PLAY_ARROW, bgcolor=ft.colors.BLUE, color=COLOR_WHITE, on_click=lambda e: atualizar_status(orcamento, "Em Andamento")))
        if status == "Em Andamento": botoes.append(ft.ElevatedButton("Finalizar", icon=ft.icons.CHECK, bgcolor=ft.colors.GREEN, color=COLOR_WHITE, on_click=lambda e: atualizar_status(orcamento, "Finalizado")))

        dlg = ft.AlertDialog(title=ft.Text(f"O.S.: {orcamento.get('cliente_nome')}", size=20, weight="bold"), content=ft.Container(width=700, content=lista), actions=[ft.TextButton("Fechar", on_click=lambda e: page.close_dialog()), *botoes], actions_alignment=ft.MainAxisAlignment.END)
        page.dialog = dlg; dlg.open = True; page.update()

    def atualizar_status(orc, novo):
        # Mudar status normal não mexe no estoque (apenas início e fim de processo)
        firebase_service.update_orcamento(orc['id'], {'status': novo})
        page.close_dialog(); carregar_dados()

    def render_coluna(status_filtro, titulo, cor_badge):
        lista = firebase_service.get_orcamentos_lista()
        filtrados = [o for o in lista if o.get('status') == status_filtro]
        grid = ft.GridView(expand=True, runs_count=3, max_extent=350, child_aspect_ratio=1.0, spacing=20, run_spacing=20)
        if not filtrados: grid.controls.append(ft.Container(padding=40, content=ft.Text("Vazio.", color=ft.colors.GREY_400)))
        else:
            for orc in filtrados:
                grid.controls.append(ft.Container(
                    bgcolor=COLOR_WHITE, border_radius=15, padding=20, shadow=ft.BoxShadow(blur_radius=5, color="#00000010"),
                    content=ft.Column([
                        ft.Row([ft.Container(content=ft.Text(status_filtro, size=10, color=COLOR_WHITE, weight="bold"), bgcolor=cor_badge, padding=5, border_radius=5), ft.Icon(ft.icons.BUILD, color="grey")]),
                        ft.Text(orc.get('cliente_nome', ''), weight="bold", size=18),
                        ft.Text(f"{len(orc.get('itens', []))} peças", size=13),
                        ft.Divider(),
                        ft.ElevatedButton("Visualizar", icon=ft.icons.VISIBILITY, bgcolor=COLOR_SECONDARY, color=COLOR_WHITE, width=float("inf"), on_click=lambda e, o=orc: abrir_visualizador(o))
                    ])
                ))
        return grid

    def carregar_dados():
        tabs = ft.Tabs(selected_index=0, animation_duration=300, tabs=[
            ft.Tab(text="1. Pendentes", icon=ft.icons.PENDING_ACTIONS, content=ft.Container(padding=20, content=render_coluna("Produção", "A Fazer", ft.colors.ORANGE))),
            ft.Tab(text="2. Em Andamento", icon=ft.icons.ENGINEERING, content=ft.Container(padding=20, content=render_coluna("Em Andamento", "Produzindo", ft.colors.BLUE))),
            ft.Tab(text="3. Finalizados", icon=ft.icons.CHECK_CIRCLE, content=ft.Container(padding=20, content=render_coluna("Finalizado", "Pronto", ft.colors.GREEN))),
        ], expand=True)
        conteudo.content = ft.Container(padding=20, expand=True, content=ft.Column([ft.Text("Produção", size=28, weight="bold", color=COLOR_PRIMARY), ft.Divider(), tabs]))
        page.update()

    carregar_dados()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Produção")