from fpdf import FPDF
import base64
from datetime import datetime
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TEXT


class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="pt", format="A4")
        self.set_auto_page_break(auto=True, margin=50)

    def header(self):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*hex_to_rgb(COLOR_PRIMARY))
        self.cell(0, 30, "CENTRAL GRANITOS", ln=True, align="C")

        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 15, "Marmoraria • Projetos Sob Medida", ln=True, align="C")
        self.ln(10)


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def gerar_pdf_orcamento(orcamento: dict) -> str | None:
    try:
        pdf = PDF()
        pdf.add_page()

        RGB_PRIMARY = hex_to_rgb(COLOR_PRIMARY)
        RGB_SECONDARY = hex_to_rgb(COLOR_SECONDARY)

        # ================= DADOS GERAIS =================
        cliente = orcamento.get("cliente_nome", "Cliente")
        contato = orcamento.get("cliente_contato", "N/A")
        numero = orcamento.get("id", "----")
        data_hoje = datetime.now().strftime("%d/%m/%Y")

        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*RGB_PRIMARY)
        pdf.cell(0, 18, "ORÇAMENTO", ln=True)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 14, f"Nº Orçamento: {numero}", ln=True)
        pdf.cell(0, 14, f"Data: {data_hoje}", ln=True)
        pdf.ln(10)

        # ================= CLIENTE =================
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 16, "DADOS DO CLIENTE", ln=True)

        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 14, f"Nome: {cliente}", ln=True)
        pdf.cell(0, 14, f"Contato: {contato}", ln=True)
        pdf.ln(10)

        # ================= ITENS =================
        total_m2_geral = 0.0

        for idx, item in enumerate(orcamento.get("itens", []), start=1):
            pdf.set_fill_color(*RGB_PRIMARY)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 10)

            qtd = int(item.get("quantidade", 1))
            titulo = f"{idx}. {item.get('ambiente')} - {item.get('material')} (Qtd: {qtd})"
            pdf.cell(0, 20, f" {titulo}", ln=True, fill=True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)

            preco = float(item.get("preco_total", 0))
            pdf.cell(
                0,
                14,
                f"Valor unitário: R$ {(preco / qtd):,.2f} | Subtotal: R$ {preco:,.2f}",
                ln=True,
            )

            # ---- Peças ----
            m2_item = 0.0
            pecas = item.get("pecas", {})

            for nome, dados in pecas.items():
                l = float(dados.get("l", 0))
                p = float(dados.get("p", 0))
                area = l * p
                m2_item += area

                pdf.cell(
                    0,
                    12,
                    f"   • {nome.upper()}: {l:.2f}m x {p:.2f}m = {area:.3f} m²",
                    ln=True,
                )

            total_m2_geral += m2_item * qtd
            pdf.cell(0, 12, f"   Área total do item: {m2_item * qtd:.3f} m²", ln=True)
            pdf.ln(6)

        # ================= TOTAL =================
        pdf.ln(15)
        pdf.set_draw_color(*RGB_SECONDARY)
        pdf.line(40, pdf.get_y(), 555, pdf.get_y())
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*RGB_PRIMARY)

        total = float(orcamento.get("total_geral", 0))
        pdf.cell(0, 22, f"TOTAL GERAL: R$ {total:,.2f}", ln=True, align="R")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 16, f"Metragem total estimada: {total_m2_geral:.3f} m²", ln=True, align="R")

        # ================= RODAPÉ =================
        pdf.ln(20)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(
            0,
            14,
            "• Orçamento válido por 7 dias.\n"
            "• Medidas sujeitas à conferência técnica no local.\n"
            "• Valores podem sofrer alteração após visita técnica.",
        )

        pdf.ln(25)
        pdf.cell(0, 14, "Assinatura do responsável: ________________________________", ln=True)

        # ================= SAÍDA =================
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        return base64.b64encode(pdf_bytes).decode("utf-8")

    except Exception as e:
        print(f"Erro ao gerar PDF do orçamento: {e}")
        return None
