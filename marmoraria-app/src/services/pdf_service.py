from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import webbrowser
import platform

def gerar_pdf_orcamento(orcamento):
    # Nome do Arquivo Seguro
    cliente_safe = orcamento.get('cliente_nome', 'Cliente').replace(" ", "_")
    filename = f"Orcamento_{cliente_safe}.pdf"
    
    # Cores (Paleta Central Granitos)
    COR_VINHO = colors.Color(0.45, 0.15, 0.15)
    COR_BRONZE = colors.Color(0.65, 0.45, 0.25)
    COR_CINZA = colors.Color(0.3, 0.3, 0.3)
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50 

    # --- 1. RESOLUÇÃO DE CAMINHO INFALÍVEL ---
    # Pega o caminho exato onde este arquivo (pdf_service.py) está
    dir_atual = os.path.dirname(os.path.abspath(__file__)) # .../src/services
    dir_src = os.path.dirname(dir_atual)                   # .../src
    dir_app = os.path.dirname(dir_src)                     # .../marmoraria-app
    
    # Monta o caminho da assets
    dir_assets = os.path.join(dir_app, 'assets')
    
    # Define os caminhos das imagens
    caminho_jpg = os.path.join(dir_assets, "logo.jpg")
    caminho_png = os.path.join(dir_assets, "logo.png")

    # Debug no Terminal (Para sabermos o que está acontecendo)
    print("-" * 30)
    print(f"Tentando encontrar logo em:")
    print(f"1. {caminho_jpg}")
    print(f"2. {caminho_png}")
    
    logo_final = None
    if os.path.exists(caminho_jpg):
        logo_final = caminho_jpg
        print("✅ LOGO JPG ENCONTRADA!")
    elif os.path.exists(caminho_png):
        logo_final = caminho_png
        print("✅ LOGO PNG ENCONTRADA!")
    else:
        print("❌ LOGO NÃO ENCONTRADA EM NENHUM LUGAR.")
    print("-" * 30)

    # --- 2. CABEÇALHO ---
    logo_desenhada = False
    
    if logo_final:
        try:
            # Desenha a logo bem grande e centralizada
            logo_width = 180  # Aumentei um pouco
            logo_height = 120 
            x_logo = (width - logo_width) / 2
            
            c.drawImage(logo_final, x_logo, height - 140, width=logo_width, preserveAspectRatio=True, mask='auto')
            logo_desenhada = True
            y -= 100 # Empurra o conteúdo para baixo
        except Exception as e:
            print(f"Erro ao desenhar imagem: {e}")

    # Se a logo NÃO apareceu, escreve o nome. Se apareceu, só coloca o contato.
    if not logo_desenhada:
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(COR_VINHO)
        c.drawCentredString(width/2, height - 60, "CENTRAL GRANITOS")
        y -= 20
    else:
        # Se tem logo, só dá um espacinho extra
        y -= 10

    # Informações de Contato (Centralizadas abaixo da logo)
    c.setFont("Helvetica", 10)
    c.setFillColor(COR_CINZA)
    c.drawCentredString(width/2, y, "Especialistas em Mármores e Granitos")
    y -= 12
    c.drawCentredString(width/2, y, "Contato: (XX) 99999-9999") 

    # Linha divisória
    y -= 20
    c.setStrokeColor(COR_BRONZE)
    c.setLineWidth(2)
    c.line(40, y, width - 40, y)
    y -= 40

    # --- 3. DADOS DO CLIENTE ---
    c.setFillColor(COR_VINHO)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "DADOS DO CLIENTE")
    
    c.setFillColor(colors.Color(0.96, 0.96, 0.96))
    c.rect(40, y - 55, width - 80, 45, fill=1, stroke=0)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y -= 25
    c.drawString(50, y, f"Cliente: {orcamento.get('cliente_nome', '-')}")
    c.drawRightString(width - 50, y, f"Contato: {orcamento.get('cliente_contato', '-')}")
    y -= 20
    c.drawString(50, y, f"Endereço: {orcamento.get('cliente_endereco', '-')}")
    
    y -= 50

    # --- 4. ITENS DO ORÇAMENTO ---
    itens = orcamento.get('itens', [])
    
    for i, item in enumerate(itens):
        if y < 280: 
            c.showPage()
            y = height - 50
        
        c.setFillColor(COR_VINHO)
        c.rect(40, y, width - 80, 22, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(45, y + 7, f"{i+1}. {item['ambiente']}  |  {item['material']}")
        c.drawRightString(width - 45, y + 7, f"R$ {item['preco_total']:.2f}")
        
        y -= 20
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(45, y - 15, f"Dimensões: {item['largura']}m x {item['profundidade']}m   |   Área Total: {item['area']:.2f} m²")
        
        # --- DESENHO TÉCNICO ---
        box_x = 100
        box_y = y - 170
        box_w = 400
        box_h = 140
        
        desenhar_item_no_pdf(c, item, box_x, box_y, box_w, box_h)
        
        y -= 190

    # --- 5. TOTAL FINAL ---
    if y < 100:
        c.showPage()
        y = height - 50

    c.setStrokeColor(COR_BRONZE)
    c.setLineWidth(2)
    c.line(40, y, width - 40, y)
    y -= 30
    
    c.setFillColor(COR_VINHO)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "TOTAL GERAL")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(width - 40, y, f"R$ {orcamento.get('total_geral', 0):.2f}")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 30, "Orçamento válido por 15 dias | Central Granitos")

    c.save()
    
    try:
        if platform.system() == "Windows":
            os.startfile(filename)
        else:
            webbrowser.open(filename)
    except:
        print(f"PDF salvo em: {filename}")
    
    return True

def desenhar_item_no_pdf(c, item, box_x, box_y, box_w, box_h):
    cfg = item.get('config', {})
    try:
        larg_real = float(item['largura'])
        prof_real = float(item['profundidade'])
    except: return

    if larg_real <= 0 or prof_real <= 0: return

    scale = min((box_w - 60) / larg_real, (box_h - 60) / prof_real) * 0.8
    w_draw = larg_real * scale
    h_draw = prof_real * scale
    
    sx = box_x + (box_w - w_draw) / 2
    sy = box_y + (box_h - h_draw) / 2
    
    C_PEDRA = colors.Color(0.92, 0.92, 0.92)
    C_RODA = colors.Color(0.8, 0.8, 0.8)
    C_SAIA = colors.Color(0.6, 0.6, 0.6)
    C_LINHA = colors.black

    c.setLineWidth(1)

    # 1. Rodabancas
    c.setFillColor(C_RODA)
    c.setStrokeColor(C_LINHA)
    def draw_roda(k, pos):
        vals = cfg.get(k, {})
        if vals.get('chk'):
            hr = float(vals.get('a', 0.10)) * scale
            if pos == 't': c.rect(sx, sy + h_draw, w_draw, hr, fill=1)
            if pos == 'b': c.rect(sx, sy - hr, w_draw, hr, fill=1)
            if pos == 'l': c.rect(sx - hr, sy, hr, h_draw, fill=1)
            if pos == 'r': c.rect(sx + w_draw, sy, hr, h_draw, fill=1)
    draw_roda('rfundo', 't'); draw_roda('rfrente', 'b'); draw_roda('resq', 'l'); draw_roda('rdir', 'r')

    # 2. Peça
    c.setFillColor(C_PEDRA)
    c.rect(sx, sy, w_draw, h_draw, fill=1, stroke=1)

    # 3. Saias
    c.setFillColor(C_SAIA)
    esp = 6
    def draw_saia(k, pos):
        vals = cfg.get(k, {})
        if vals.get('chk'):
            if pos == 't': c.rect(sx, sy + h_draw - esp, w_draw, esp, fill=1, stroke=0)
            if pos == 'b': c.rect(sx, sy, w_draw, esp, fill=1, stroke=0)
            if pos == 'l': c.rect(sx, sy, esp, h_draw, fill=1, stroke=0)
            if pos == 'r': c.rect(sx + w_draw - esp, sy, esp, h_draw, fill=1, stroke=0)
    draw_saia('sfundo', 't'); draw_saia('sfrente', 'b'); draw_saia('sesq', 'l'); draw_saia('sdir', 'r')

    # 4. Recortes
    c.setFillColor(colors.white)
    cuba = cfg.get('cuba', {})
    if cuba.get('chk'):
        dist = float(cuba.get('pos', 0)) * scale
        cw, ch = w_draw * 0.4, h_draw * 0.6
        c.roundRect(sx + dist, sy + (h_draw - ch)/2, cw, ch, 4, fill=0, stroke=1)
        c.circle(sx + dist + cw/2, sy + (h_draw - ch)/2 + ch - 8, 3, fill=0, stroke=1)

    cook = cfg.get('cook', {})
    if cook.get('chk'):
        dist = float(cook.get('pos', 0)) * scale
        cw, ch = w_draw * 0.35, h_draw * 0.6
        cx, cy = sx + dist, sy + (h_draw - ch)/2
        c.rect(cx, cy, cw, ch, fill=0, stroke=1)
        c.circle(cx + cw*0.25, cy + ch*0.25, 4, stroke=1)
        c.circle(cx + cw*0.75, cy + ch*0.75, 4, stroke=1)

    # 5. Cotas
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawCentredString(sx + w_draw/2, sy - 12, f"{larg_real}m")
    c.drawString(sx - 35, sy + h_draw/2, f"{prof_real}m")