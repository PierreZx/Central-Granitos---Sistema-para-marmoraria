import flet as ft
import flet.canvas as cv
from math import fabs

class BudgetCalculator(ft.Container):
    def __init__(self, page, on_save_item, on_cancel):
        super().__init__(expand=True)
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel

        # ---------------- DADOS ----------------
        self.segmentos = []
        self.cuba = None

        # ---------------- INPUTS ----------------
        self.txt_ambiente = ft.TextField(label="Ambiente")
        self.txt_material = ft.TextField(label="Material")
        self.txt_preco_m2 = ft.TextField(label="Preço m²", keyboard_type=ft.KeyboardType.NUMBER)

        self.comp = ft.TextField(label="Comprimento (m)")
        self.prof = ft.TextField(label="Profundidade (m)")

        self.canvas = cv.Canvas(width=360, height=240)

        self.lbl_area = ft.Text("Área: 0.00 m²", weight="bold")
        self.lbl_total = ft.Text("Total: R$ 0.00", size=18, weight="bold")

        # ---------------- BOTÕES ----------------
        btn_add = ft.ElevatedButton("Adicionar Segmento", on_click=self.add_segmento)
        btn_cuba = ft.ElevatedButton("Adicionar Cuba", on_click=self.add_cuba)

        btn_salvar = ft.ElevatedButton("Salvar", on_click=self.salvar)
        btn_cancelar = ft.TextButton("Cancelar", on_click=self.on_cancel)

        self.content = ft.Column([
            self.txt_ambiente,
            self.txt_material,
            self.txt_preco_m2,

            ft.Text("Segmentos da Bancada"),
            ft.Row([self.comp, self.prof, btn_add]),

            ft.Container(self.canvas, bgcolor="#F5F5F5", padding=10),

            btn_cuba,
            self.lbl_area,
            self.lbl_total,

            ft.Row([btn_cancelar, btn_salvar], alignment="end")
        ], scroll=ft.ScrollMode.AUTO)

    # ---------------- GEOMETRIA ----------------
    def gerar_poligono(self):
        pontos = [(0, 0)]
        x, y = 0, 0

        for s in self.segmentos:
            x += s["comp"]
            pontos.append((x, y))
            y += s["prof"]
            pontos.append((x, y))

        pontos.append((0, y))
        return pontos

    def area_poligono(self, pts):
        area = 0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i+1) % len(pts)]
            area += x1*y2 - x2*y1
        return fabs(area) / 2

    # ---------------- DESENHO ----------------
    def iso(self, x, y, z=0):
        return x - y, (x + y)/2 - z

    def desenhar(self):
        self.canvas.shapes.clear()
        pts = self.gerar_poligono()
        if len(pts) < 3:
            self.canvas.update()
            return

        escala = 80
        ox, oy = 180, 120

        iso_pts = []
        for x, y in pts:
            ix, iy = self.iso(x*escala, y*escala)
            iso_pts.append((ox+ix, oy+iy))

        for i in range(len(iso_pts)):
            x1,y1 = iso_pts[i]
            x2,y2 = iso_pts[(i+1)%len(iso_pts)]
            self.canvas.shapes.append(
                cv.Line(x1,y1,x2,y2, paint=ft.Paint(color="black", stroke_width=2))
            )

        if self.cuba:
            cx, cy = self.iso(self.cuba["x"]*escala, self.cuba["y"]*escala)
            self.canvas.shapes.append(
                cv.Rect(ox+cx, oy+cy, 40, 25,
                    paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="blue", stroke_width=2))
            )

        self.canvas.update()

    # ---------------- AÇÕES ----------------
    def add_segmento(self, e):
        try:
            self.segmentos.append({
                "comp": float(self.comp.value.replace(",",".")),
                "prof": float(self.prof.value.replace(",",".")),
            })
            self.comp.value = ""
            self.prof.value = ""
            self.atualizar()
        except:
            pass

    def add_cuba(self, e):
        self.cuba = {"x": 0.6, "y": 0.3}
        self.desenhar()

    def atualizar(self):
        pts = self.gerar_poligono()
        area = self.area_poligono(pts)
        preco = float(self.txt_preco_m2.value.replace(",",".")) if self.txt_preco_m2.value else 0
        total = area * preco

        self.lbl_area.value = f"Área: {area:.2f} m²"
        self.lbl_total.value = f"Total: R$ {total:,.2f}"
        self.desenhar()
        self.page.update()

    def salvar(self, e):
        item = {
            "ambiente": self.txt_ambiente.value,
            "material": self.txt_material.value,
            "area": float(self.lbl_area.value.split()[1]),
            "preco_total": float(self.lbl_total.value.replace("R$","").replace(",",""))
        }
        self.on_save_item(item)
