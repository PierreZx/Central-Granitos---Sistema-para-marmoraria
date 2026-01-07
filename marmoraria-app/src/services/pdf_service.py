from fpdf import FPDF
import os
import platform
import webbrowser

class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='pt', format='A4')
        self.set_auto_page_break(auto=True, margin=40)

def gerar_pdf_orcamento(orcamento):
    cliente_safe = orcamento.get('cliente_nome', 'Cliente').replace(" ", "_")
    filename = f"Orcamento_{cliente_safe}.pdf"
    
    # Cores (RGB)
    COR_VINHO = (115, 38, 38)
    COR_CINZA = (80, 80, 80)
    
    # Configuração Inicial
    pdf = PDF()
    pdf.add_page()
    # Tamanho A4 em points (aprox)
    width, height = 595.28, 841.89 
    
    # --- 1. LOGO E CABEÇALHO ---
    y = 40 
    
    dir_atual = os.path.dirname(os.path.abspath(__file__)) 
    # Sobe duas pastas para achar o assets (src/services -> src -> raiz -> assets)
    # Ajuste conforme sua estrutura real. Se assets está na raiz:
    dir_assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(dir_atual))), 'assets')
    if not os.path.exists(dir_assets):
        # Tenta pegar relativo ao script se a estrutura for diferente
        dir_assets = "assets"

    caminho_jpg = os.path.join(dir_assets, "logo.jpg")
    caminho_png = os.path.join(dir_assets, "logo.png")
    logo_final = caminho_jpg if os.path.exists(caminho_jpg) else caminho_png if os.path.exists(caminho_png) else None

    if logo_final:
        try:
            # x, y, w, h
            pdf.image(logo_final, x=(width-180)/2, y=y, w=180)
            y += 110
        except: 
            pass
    else:
        # Texto se não achar logo
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(*COR_VINHO)
        pdf.cell(0, 30, "CENTRAL GRANITOS", align="C", ln=True)
        y += 40

    pdf.set_y(y)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COR_CINZA)
    pdf.cell(0, 14, "Especialistas em Mármores e Granitos", align="C", ln=True)
    pdf.cell(0, 14, "Contato: (XX) 99999-9999", align="C", ln=True)
    
    y = pdf.get_y() + 10
    pdf.set_draw_color(165, 115, 65) # Bronze
    pdf.set_line_width(2)
    pdf.line(40, y, width - 40, y)
    y += 20

    # --- 2. DADOS CLIENTE ---
    pdf.set_y(y)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*COR_VINHO)
    pdf.cell(0, 20, "DADOS DO CLIENTE", ln=True)
    
    y_box = pdf.get_y()
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(40, y_box, width - 80, 55, 'F')
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(50, y_box + 10)
    pdf.cell(0, 16, f"Cliente: {orcamento.get('cliente_nome', '-')}", ln=True)
    pdf.set_x(50)
    pdf.cell(0, 16, f"Contato: {orcamento.get('cliente_contato', '-')}", ln=True)
    pdf.set_x(50)
    pdf.cell(0, 16, f"Endereço: {orcamento.get('cliente_endereco', '-')}", ln=True)
    
    y = y_box + 70

    # --- 3. ITENS ---
    itens = orcamento.get('itens', [])
    for i, item in enumerate(itens):
        if y > height - 250:
            pdf.add_page()
            y = 40
            
        cfg = item.get('config', {})
        
        # Faixa Vinho
        pdf.set_fill_color(*COR_VINHO)
        pdf.rect(40, y, width - 80, 25, 'F')
        
        pdf.set_xy(45, y + 5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(255, 255, 255)
        texto_item = f"{i+1}. {item['ambiente']}  |  {item['material']}"
        pdf.cell(300, 15, texto_item)
        
        pdf.set_x(width - 150)
        pdf.cell(100, 15, f"R$ {item['preco_total']:.2f}", align="R")
        
        y += 35
        
        # Detalhes
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(45, y)
        pdf.cell(0, 15, f"Medidas: {item['largura']}m x {item['profundidade']}m   |   Area: {item['area']:.2f} m2", ln=True)
        
        borda = cfg.get('tipo_borda', 'Reto')
        obs = cfg.get('obs', '')
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(45)
        pdf.write(15, f"Acabamento: {borda}   ")
        
        if obs:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(200, 0, 0)
            pdf.write(15, f"OBS: {obs}")
            
        y += 20
        
        # Desenho
        box_h = 140
        desenhar_item_fpdf(pdf, item, 100, y, 400, box_h)
        y += box_h + 30

    # --- 4. TOTAL ---
    if y > height - 100: pdf.add_page(); y = 40
    
    pdf.set_draw_color(165, 115, 65)
    pdf.line(40, y, width - 40, y)
    y += 20
    
    pdf.set_xy(40, y)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VINHO)
    pdf.cell(200, 30, "TOTAL GERAL")
    
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(width - 200)
    pdf.cell(150, 30, f"R$ {orcamento.get('total_geral', 0):.2f}", align="R")
    
    pdf.set_y(height - 40)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Orcamento valido por 15 dias | Central Granitos", align="C")

    pdf.output(filename)
    
    # Abre o PDF (Android tenta abrir com app padrão)
    try:
        if platform.system() == "Windows": os.startfile(filename)
        else: webbrowser.open(filename)
    except: pass
    return True

def desenhar_item_fpdf(pdf, item, box_x, box_y, box_w, box_h):
    try: larg_real = float(item['largura']); prof_real = float(item['profundidade'])
    except: return
    
    if larg_real <= 0 or prof_real <= 0: return
    
    scale = min((box_w - 60) / larg_real, (box_h - 60) / prof_real) * 0.8
    w_draw = larg_real * scale; h_draw = prof_real * scale
    sx = box_x + (box_w - w_draw) / 2; sy = box_y + (box_h - h_draw) / 2
    
    pdf.set_line_width(1)
    cfg = item.get('config', {})
    
    # Rodas
    pdf.set_fill_color(200, 200, 200) 
    def draw_roda(k, pos):
        vals = cfg.get(k, {})
        if vals.get('chk'):
            hr = float(vals.get('a', 0.10)) * scale
            if pos == 't': pdf.rect(sx, sy - hr, w_draw, hr, 'F')
            if pos == 'b': pdf.rect(sx, sy + h_draw, w_draw, hr, 'F')
            if pos == 'l': pdf.rect(sx - hr, sy, hr, h_draw, 'F')
            if pos == 'r': pdf.rect(sx + w_draw, sy, hr, h_draw, 'F')
    draw_roda('rfundo', 't'); draw_roda('rfrente', 'b')
    draw_roda('resq', 'l'); draw_roda('rdir', 'r')

    # Pedra
    pdf.set_fill_color(235, 235, 235)
    pdf.rect(sx, sy, w_draw, h_draw, 'FD')
    
    # Saia
    pdf.set_fill_color(150, 150, 150)
    esp = 6
    def draw_saia(k, pos):
        vals = cfg.get(k, {})
        if vals.get('chk'):
            if pos == 't': pdf.rect(sx, sy, w_draw, esp, 'F')
            if pos == 'b': pdf.rect(sx, sy + h_draw - esp, w_draw, esp, 'F')
            if pos == 'l': pdf.rect(sx, sy, esp, h_draw, 'F')
            if pos == 'r': pdf.rect(sx + w_draw - esp, sy, esp, h_draw, 'F')
    draw_saia('sfundo', 't'); draw_saia('sfrente', 'b')
    draw_saia('sesq', 'l'); draw_saia('sdir', 'r')

    # Cortes
    pdf.set_fill_color(255, 255, 255)
    cuba = cfg.get('cuba', {})
    if cuba.get('chk'):
        dist = float(cuba.get('pos', 0)) * scale
        cw = float(cuba.get('larg', 0.5)) * scale
        ch = float(cuba.get('prof', 0.4)) * scale
        cy = sy + (h_draw - ch) / 2
        pdf.rect(sx + dist, cy, cw, ch, 'D')
        pdf.ellipse(sx + dist + cw/2 - 3, cy + ch - 8, 6, 6, 'D')

    cook = cfg.get('cook', {})
    if cook.get('chk'):
        dist = float(cook.get('pos', 0)) * scale
        cw = float(cook.get('larg', 0.6)) * scale
        ch = float(cook.get('prof', 0.45)) * scale
        cy = sy + (h_draw - ch) / 2
        cx = sx + dist
        pdf.rect(cx, cy, cw, ch, 'D')
        pdf.ellipse(cx + cw*0.25, cy + ch*0.25, 8, 8, 'D')
        pdf.ellipse(cx + cw*0.75, cy + ch*0.75, 8, 8, 'D')

    # Cotas
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.text(sx + w_draw/2 - 10, sy - 5, f"{larg_real}m")
    pdf.text(sx - 35, sy + h_draw/2, f"{prof_real}m")