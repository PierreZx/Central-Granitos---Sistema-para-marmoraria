import flet as ft
import flet.canvas as cv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.pagesizes import A4
from src.services import firebase_service
import math
import uuid

# ======================================================
# MODELOS DE DADOS
# ======================================================

class Segmento:
    def __init__(self, x, y, comp, prof):
        self.x = x
        self.y = y
        self.comp = comp
        self.prof = prof

class Cuba:
    def __init__(self, x, y, w=0.50, h=0.40):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Recorte:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

# ======================================================
# CALCULADORA
# ======================================================

class BudgetCalculator(ft.Container):
    def __init__(self, page, on_save_item, on_cancel):
        super().__init__(expand=True)
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel

        # ================= ESTADO =================
        self.segmentos = []
        self.cubas = []
        self.recortes = []

        self.saiam = 0.0
        self.rodabanca = 0.0
        self.preco_m2 = 0.0
        self.material = ""

        # ================= CAMPOS =================
        self.dd_tipo = ft.Dropdown(
            label="Tipo de bancada",
            options=[
                ft.dropdown.Option("RETA"),
                ft.dropdown.Option("L"),
                ft.dropdown.Option("U")
            ],
            value="RETA"
        )

        self.txt_comp = ft.TextField(label="Comprimento (m)")
        self.txt_prof = ft.TextField(label="Profundidade (m)")

        self.txt_saia = ft.TextField(label="Altura da Saia (m)", value="0.10")
        self.txt_rodabanca = ft.TextField(label="Altura da Rodabanca (m)", value="0.07")

        self.dd_material = ft.Dropdown(label="Material")
        self.txt_preco = ft.TextField(label="Preço m²", disabled=True)

        self.lbl_area = ft.Text(weight="bold")
        self.lbl_total = ft.Text(size=18, weight="bold")

        # ================= CANVAS =================
        self.canvas = cv.Canvas(height=280)

        # ================= BOTÕES =================
        btn_gerar = ft.ElevatedButton("Gerar Bancada", on_click=self.gerar_bancada)
        btn_cuba = ft.ElevatedButton("Adicionar Cuba", on_click=self.add_cuba)
        btn_recorte = ft.ElevatedButton("Adicionar Recorte", on_click=self.add_recorte)
        btn_pdf = ft.ElevatedButton("Gerar PDF Técnico", on_click=self.gerar_pdf)

        btn_salvar = ft.ElevatedButton("Salvar", on_click=self.salvar)
        btn_cancelar = ft.TextButton("Cancelar", on_click=self.on_cancel)

        self.content = ft.Column([
            self.dd_tipo,
            ft.Row([self.txt_comp, self.txt_prof]),
            ft.Row([self.txt_saia, self.txt_rodabanca]),
            self.dd_material,
            self.txt_preco,
            btn_gerar,
            self.canvas,
            ft.Row([btn_cuba, btn_recorte]),
            self.lbl_area,
            self.lbl_total,
            ft.Row([btn_cancelar, btn_salvar, btn_pdf])
        ], scroll=ft.ScrollMode.AUTO)

        self.carregar_materiais()

    # ======================================================
    # ESTOQUE
    # ======================================================

    def carregar_materiais(self):
        itens = firebase_service.get_collection("estoque")
        self.dd_material.options = [
            ft.dropdown.Option(key=i["id"], text=i["nome"]) for i in itens
        ]
        self.dd_material.on_change = self.selecionar_material

    def selecionar_material(self, e):
        item = next(i for i in firebase_service.get_collection("estoque") if i["id"] == e.control.value)
        self.material = item["nome"]
        self.preco_m2 = float(item.get("preco_m2", 0))
        self.txt_preco.value = f"{self.preco_m2:.2f}"
        self.page.update()

    # ======================================================
    # GEOMETRIA
    # ======================================================

    def gerar_bancada(self, e):
        self.segmentos.clear()
        self.cubas.clear()
        self.recortes.clear()

        c = float(self.txt_comp.value)
        p = float(self.txt_prof.value)

        if p < 0.55:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Profundidade mínima 55cm"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        tipo = self.dd_tipo.value

        if tipo == "RETA":
            self.segmentos.append(Segmento(0, 0, c, p))

        elif tipo == "L":
            self.segmentos.append(Segmento(0, 0, c, p))
            self.segmentos.append(Segmento(c - p, p, p, c / 2))

        elif tipo == "U":
            self.segmentos.append(Segmento(0, 0, c, p))
            self.segmentos.append(Segmento(0, p, p, c))
            self.segmentos.append(Segmento(c - p, p, p, c))

        self.atualizar()

    def area_total(self):
        area = sum(s.comp * s.prof for s in self.segmentos)
        for r in self.recortes:
            area -= r.w * r.h
        return area

    def area_saia(self):
        altura = float(self.txt_saia.value)
        return sum(s.comp * altura for s in self.segmentos)

    def area_rodabanca(self):
        altura = float(self.txt_rodabanca.value)
        return sum(s.comp * altura for s in self.segmentos)

    # ======================================================
    # DESENHO
    # ======================================================

    def desenhar(self):
        self.canvas.shapes.clear()
        escala = 80
        ox, oy = 20, 40

        for s in self.segmentos:
            self.canvas.shapes.append(
                cv.Rect(
                    ox + s.x * escala,
                    oy + s.y * escala,
                    s.comp * escala,
                    s.prof * escala,
                    paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2)
                )
            )

        for c in self.cubas:
            self.canvas.shapes.append(
                cv.Rect(
                    ox + c.x * escala,
                    oy + c.y * escala,
                    c.w * escala,
                    c.h * escala,
                    paint=ft.Paint(color="blue", style=ft.PaintingStyle.STROKE)
                )
            )

        for r in self.recortes:
            self.canvas.shapes.append(
                cv.Rect(
                    ox + r.x * escala,
                    oy + r.y * escala,
                    r.w * escala,
                    r.h * escala,
                    paint=ft.Paint(color="red", style=ft.PaintingStyle.STROKE)
                )
            )

        self.canvas.update()

    # ======================================================
    # AÇÕES
    # ======================================================

    def add_cuba(self, e):
        s = self.segmentos[0]
        self.cubas.append(Cuba(
            s.x + s.comp / 2 - 0.25,
            s.y + 0.10
        ))
        self.atualizar()

    def add_recorte(self, e):
        s = self.segmentos[0]
        self.recortes.append(Recorte(
            s.x + s.comp - 0.60,
            s.y + 0.10,
            0.50,
            0.40
        ))
        self.atualizar()

    def atualizar(self):
        area = self.area_total()
        total = (
            area * self.preco_m2 +
            self.area_saia() * self.preco_m2 +
            self.area_rodabanca() * self.preco_m2
        )

        self.lbl_area.value = f"Área total: {area:.2f} m²"
        self.lbl_total.value = f"Total: R$ {total:,.2f}"

        self.desenhar()
        self.page.update()

    # ======================================================
    # PDF TÉCNICO
    # ======================================================

    def gerar_pdf(self, e):
        path = f"/mnt/data/orcamento_{uuid.uuid4().hex}.pdf"
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>Projeto de Bancada</b>", styles["Title"]))
        story.append(Paragraph(f"Material: {self.material}", styles["Normal"]))
        story.append(Paragraph(f"Área: {self.area_total():.2f} m²", styles["Normal"]))

        d = Drawing(400, 200)
        for s in self.segmentos:
            d.add(Rect(
                s.x * 100,
                s.y * 100,
                s.comp * 100,
                s.prof * 100,
                strokeWidth=2
            ))

        story.append(d)
        doc.build(story)

        self.page.snack_bar = ft.SnackBar(ft.Text("📄 PDF gerado com sucesso"))
        self.page.snack_bar.open = True
        self.page.update()

    # ======================================================
    # SALVAR
    # ======================================================

    def salvar(self, e):
        self.on_save_item({
            "area": self.area_total(),
            "material": self.material
        })
