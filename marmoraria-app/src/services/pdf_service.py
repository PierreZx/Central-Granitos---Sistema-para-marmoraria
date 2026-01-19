# src/services/pdf_service.py
from fpdf import FPDF
import os
import platform
import webbrowser
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TEXT

class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='pt', format='A4')
        self.set_auto_page_break(auto=True, margin=50)

def gerar_pdf_orcamento(orcamento: dict) -> bool:
    cliente_nome = orcamento.get('cliente_nome', 'Cliente')
    filename = f"Orcamento_{cliente_nome.replace(' ', '_')}.pdf"

    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    RGB_VINHO = hex_to_rgb(COLOR_PRIMARY)
    pdf = PDF()
    pdf.add_page()
    width, height = 595.28, 841.89

    # Cabeçalho
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*RGB_VINHO)
    pdf.cell(0, 40, "CENTRAL GRANITOS", align="C", ln=True)
    
    # Info Cliente
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 20, "INFORMAÇÕES DO CLIENTE", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 14, f"Nome: {cliente_nome}", ln=True)
    pdf.cell(0, 14, f"Contato: {orcamento.get('cliente_contato', 'N/A')}", ln=True)
    pdf.ln(10)

    # Listagem de itens
    for i, item in enumerate(orcamento.get('itens', [])):
        pdf.set_fill_color(*RGB_VINHO)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        qtd = item.get('quantidade', 1)
        pdf.cell(0, 20, f" {i+1}. {item.get('ambiente')} - {item.get('material')} (Qtd: {qtd})", ln=True, fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        preco = float(item.get('preco_total', 0))
        pdf.cell(0, 15, f"Valor Unitário: R$ {(preco/qtd):,.2f} | Subtotal: R$ {preco:,.2f}", ln=True)

        # Detalhes das peças
        pecas = item.get('pecas', {})
        for nome_p, dados in pecas.items():
            pdf.cell(0, 12, f"  > {nome_p.upper()}: {dados.get('l')}m x {dados.get('p')}m", ln=True)
        
        pdf.ln(5)

    # Total
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*RGB_VINHO)
    total = float(orcamento.get('total_geral', 0))
    pdf.cell(0, 30, f"TOTAL GERAL: R$ {total:,.2f}", align="R", ln=True)

    try:
        pdf.output(filename)
        webbrowser.open(filename)
        return True
    except Exception as e:
        print(f"Erro PDF: {e}")
        return False