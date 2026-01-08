from fpdf import FPDF
import os
import platform
import webbrowser
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TEXT

class PDF(FPDF):
    def __init__(self):
        # Unidades em pontos (pt) são ótimas para precisão de layout
        super().__init__(orientation='P', unit='pt', format='A4')
        self.set_auto_page_break(auto=True, margin=50)

def gerar_pdf_orcamento(orcamento):
    cliente_nome = orcamento.get('cliente_nome', 'Cliente')
    cliente_safe = cliente_nome.replace(" ", "_")
    filename = f"Orcamento_{cliente_safe}.pdf"
    
    # Conversão de HEX para RGB para o FPDF
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    RGB_VINHO = hex_to_rgb(COLOR_PRIMARY)
    RGB_BRONZE = hex_to_rgb(COLOR_SECONDARY)
    RGB_TEXTO = hex_to_rgb(COLOR_TEXT)
    
    pdf = PDF()
    pdf.add_page()
    width, height = 595.28, 841.89 
    
    # --- 1. CABEÇALHO E LOGO ---
    # Busca a logo em várias pastas possíveis para evitar erro de caminho
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    paths_to_try = [
        os.path.join(base_dir, "assets", "logo.png"),
        os.path.join(base_dir, "assets", "logo.jpg"),
        "assets/logo.png"
    ]
    
    logo_final = next((p for p in paths_to_try if os.path.exists(p)), None)
    y = 40

    if logo_final:
        pdf.image(logo_final, x=(width-150)/2, y=y, w=150)
        y += 100
    else:
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(*RGB_VINHO)
        pdf.set_xy(0, y)
        pdf.cell(width, 30, "CENTRAL GRANITOS", align="C", ln=True)
        y += 40

    pdf.set_y(y)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 14, "Marmoraria e Marmoraria - Qualidade em cada detalhe", align="C", ln=True)
    
    y = pdf.get_y() + 10
    pdf.set_draw_color(*RGB_BRONZE)
    pdf.set_line_width(1.5)
    pdf.line(40, y, width - 40, y)
    y += 25

    # --- 2. ÁREA DO CLIENTE ---
    pdf.set_y(y)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*RGB_VINHO)
    pdf.cell(0, 20, "INFORMAÇÕES DO CLIENTE", ln=True)
    
    pdf.set_fill_color(250, 248, 245) # Fundo levemente creme
    pdf.rect(40, pdf.get_y(), width - 80, 50, 'F')
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*RGB_TEXTO)
    pdf.set_xy(50, pdf.get_y() + 8)
    pdf.cell(0, 14, f"Nome: {cliente_nome}", ln=True)
    pdf.set_x(50)
    pdf.cell(0, 14, f"Contato: {orcamento.get('cliente_contato', 'N/A')}", ln=True)
    pdf.set_x(50)
    pdf.cell(0, 14, f"Endereço: {orcamento.get('cliente_endereco', 'Não informado')}", ln=True)
    
    y = pdf.get_y() + 25

    # --- 3. LISTAGEM DE ITENS (ORÇAMENTO) ---
    itens = orcamento.get('itens', [])
    for i, item in enumerate(itens):
        # Checa se precisa de nova página antes de desenhar o item
        if y > height - 200:
            pdf.add_page()
            y = 50

        # Título do Item (Ambiente | Material)
        pdf.set_fill_color(*RGB_VINHO)
        pdf.rect(40, y, width - 80, 22, 'F')
        
        pdf.set_xy(45, y + 4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(300, 15, f"{i+1}. {item.get('ambiente', 'Item')} - {item.get('material', 'Pedra')}")
        
        pdf.set_x(width - 150)
        preco = float(item.get('preco_total', 0))
        pdf.cell(100, 15, f"R$ {preco:,.2f}", align="R")
        
        y += 30
        
        # Especificações Técnicas
        pdf.set_text_color(*RGB_TEXTO)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(45, y)
        medidas = f"Dimensões: {item.get('largura')}m x {item.get('profundidade')}m  |  Área Total: {item.get('area', 0):.2f} m²"
        pdf.cell(0, 12, medidas, ln=True)
        
        y = pdf.get_y() + 5
        # Desenho Técnico do Item
        box_h = 130
        desenhar_item_fpdf(pdf, item, 40, y, width - 80, box_h)
        y += box_h + 20

    # --- 4. RODAPÉ E TOTAL ---
    if y > height - 120:
        pdf.add_page()
        y = 50

    pdf.set_draw_color(*RGB_BRONZE)
    pdf.line(40, y, width - 40, y)
    y += 15
    
    pdf.set_xy(40, y)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*RGB_VINHO)
    pdf.cell(200, 30, "VALOR TOTAL DO PROJETO")
    
    total = float(orcamento.get('total_geral', 0))
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*RGB_TEXTO)
    pdf.set_x(width - 240)
    pdf.cell(200, 30, f"R$ {total:,.2f}", align="R")
    
    # Assinaturas e Validade
    y += 60
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(40, y)
    pdf.multi_cell(width-80, 10, "Observações: Orçamento válido por 10 dias. O prazo de entrega começa a contar após a medição final e aprovação do projeto executivo.", align="C")

    # Gerar arquivo
    try:
        pdf.output(filename)
        if platform.system() == "Windows": os.startfile(filename)
        else: webbrowser.open(filename)
        return True
    except Exception as e:
        print(f"Erro ao salvar PDF: {e}")
        return False

def desenhar_item_fpdf(pdf, item, box_x, box_y, box_w, box_h):
    """Desenha a representação técnica da pedra no PDF"""
    try:
        larg = float(str(item.get('largura')).replace(',', '.'))
        prof = float(str(item.get('profundidade')).replace(',', '.'))
        
        # Fundo do desenho (box de visualização)
        pdf.set_fill_color(252, 252, 252)
        pdf.set_draw_color(230, 230, 230)
        pdf.rect(box_x, box_y, box_w, box_h, 'FD')

        # Escala automática
        scale = min((box_w - 60) / larg, (box_h - 60) / prof)
        w_px = larg * scale
        h_px = prof * scale
        
        # Centraliza o desenho dentro da box
        offset_x = box_x + (box_w - w_px) / 2
        offset_y = box_y + (box_h - h_px) / 2

        # Pedra Principal
        pdf.set_fill_color(220, 220, 220)
        pdf.set_draw_color(50, 50, 50)
        pdf.set_line_width(0.5)
        pdf.rect(offset_x, offset_y, w_px, h_px, 'FD')

        # Cotas (Medidas no desenho)
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "", 8)
        pdf.text(offset_x + (w_px/2) - 10, offset_y - 5, f"{larg}m")
        pdf.text(offset_x - 30, offset_y + (h_px/2), f"{prof}m")

    except:
        pdf.text(box_x + 10, box_y + 20, "Visualização técnica indisponível")