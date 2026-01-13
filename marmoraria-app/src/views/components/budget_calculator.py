import flet as ft
import flet.canvas as cv
from math import fabs
from src.services import firebase_service


class BudgetCalculator(ft.Container):
    def __init__(self, page, on_save_item, on_cancel):
        super().__init__(expand=True)
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel

        # ================== DADOS ==================
        self.segmentos = []        # [{comp, prof}]
        self.recortes = []         # [{x,y,w,h}]
        self.cuba = None           # {x,y,w,h}
        self.material_atual = None
        self.arrastando = None

        # ================== INPUTS ==================
        self.txt_ambiente = ft.TextField(label="Ambiente", filled=True)
        self.dd_material = ft.Dropdown(label="Material (estoque)", filled=True)
        self.txt_preco_m2 = ft.TextField(label="Preço m²", disabled=True)

        self.comp = ft.TextField(label="Comprimento (m)", expand=True)
        self.prof = ft.TextField(label="Profundidade (m)", expand=True)

        self.canvas = cv.Canvas(
            width=360,
            height=260
        )

        self.gesture = ft.GestureDetector(
            on_pan_start=self.pan_start,
            on_pan_update=self.pan_update,
            on_pan_end=self.pan_end,
            content=self.canvas
        )

        self.lbl_area = ft.Text("Área: 0.00 m²", weight="bold")
        self.lbl_total = ft.Text("Total: R$ 0.00", size=18, weight="bold")

        # ================== BOTÕES ==================
        btn_add_seg = ft.ElevatedButton("Adicionar Segmento", on_click=self.add_segmento)
        btn_add_rec = ft.ElevatedButton("Adicionar Recorte", on_click=self.add_recorte)
        btn_add_cuba = ft.ElevatedButton("Adicionar Cuba", on_click=self.add_cuba)

        btn_salvar = ft.ElevatedButton("Salvar Item", on_click=self.salvar)
        btn_cancelar = ft.TextButton("Cancelar", on_click=self.on_cancel)

        # ================== LAYOUT ==================
        self.content = ft.Column([
            self.txt_ambiente,
            self.dd_material,
            self.txt_preco_m2,

            ft.Text("Segmentos da Bancada", weight="bold"),
            ft.Row([self.comp, self.prof, btn_add_seg]),

            ft.Container(
                self.gesture,
                bgcolor="#F5F5F5",
                padding=8,
                border_radius=10
            ),


            ft.Row([btn_add_cuba, btn_add_rec], alignment="spaceBetween"),

            self.lbl_area,
            self.lbl_total,

            ft.Row([btn_cancelar, btn_salvar], alignment="end")
        ], scroll=ft.ScrollMode.AUTO)

        self.carregar_materiais()

    # ================== ESTOQUE ==================
    def carregar_materiais(self):
        materiais = firebase_service.get_collection("estoque")
        self.dd_material.options = []
        for m in materiais:
            self.dd_material.options.append(
                ft.dropdown.Option(
                    key=m["id"],
                    text=f'{m["nome"]} - R$ {m.get("preco_m2",0):,.2f}'
                )
            )
        self.dd_material.on_change = self.selecionar_material

    def selecionar_material(self, e):
        item = firebase_service.get_document("estoque", e.control.value)
        self.material_atual = item
        self.txt_preco_m2.value = f'{item.get("preco_m2",0):.2f}'
        self.atualizar()

    # ================== GEOMETRIA ==================
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
            x2, y2 = pts[(i + 1) % len(pts)]
            area += x1 * y2 - x2 * y1
        return fabs(area) / 2

    # ================== DESENHO ==================
    def iso(self, x, y):
        return x - y, (x + y) / 2

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
            ix, iy = self.iso(x * escala, y * escala)
            iso_pts.append((ox + ix, oy + iy))

        # Bancada
        for i in range(len(iso_pts)):
            x1, y1 = iso_pts[i]
            x2, y2 = iso_pts[(i + 1) % len(iso_pts)]
            self.canvas.shapes.append(
                cv.Line(x1, y1, x2, y2, paint=ft.Paint(stroke_width=2))
            )

        # Recortes
        for r in self.recortes:
            rx, ry = self.iso(r["x"] * escala, r["y"] * escala)
            rw = r["w"] * escala
            rh = r["h"] * escala
            self.canvas.shapes.append(
                cv.Rect(
                    ox + rx, oy + ry, rw, rh,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        color="red",
                        stroke_width=2
                    )
                )
            )

        # Cuba
        if self.cuba:
            cx, cy = self.iso(self.cuba["x"] * escala, self.cuba["y"] * escala)
            self.canvas.shapes.append(
                cv.Rect(
                    ox + cx, oy + cy,
                    self.cuba["w"] * escala,
                    self.cuba["h"] * escala,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        color="blue",
                        stroke_width=2
                    )
                )
            )

        self.canvas.update()

    # ================== INTERAÇÃO ==================
    def pan_start(self, e):
        self.arrastando = "cuba" if self.cuba else None

    def pan_update(self, e):
        if self.arrastando == "cuba":
            self.cuba["x"] += e.delta_x / 80
            self.cuba["y"] += e.delta_y / 80
            self.desenhar()

    def pan_end(self, e):
        self.arrastando = None

    # ================== AÇÕES ==================
    def add_segmento(self, e):
        try:
            self.segmentos.append({
                "comp": float(self.comp.value.replace(",", ".")),
                "prof": float(self.prof.value.replace(",", "."))
            })
            self.comp.value = ""
            self.prof.value = ""
            self.atualizar()
        except:
            pass

    def add_recorte(self, e):
        self.recortes.append({"x": 0.3, "y": 0.3, "w": 0.2, "h": 0.2})
        self.atualizar()

    def add_cuba(self, e):
        self.cuba = {"x": 0.4, "y": 0.2, "w": 0.4, "h": 0.25}
        self.desenhar()

    def atualizar(self):
        pts = self.gerar_poligono()
        area = self.area_poligono(pts)

        for r in self.recortes:
            area -= r["w"] * r["h"]

        preco = float(self.txt_preco_m2.value.replace(",", ".")) if self.txt_preco_m2.value else 0
        total = area * preco

        self.lbl_area.value = f"Área: {area:.2f} m²"
        self.lbl_total.value = f"Total: R$ {total:,.2f}"

        self.desenhar()
        self.page.update()

    def salvar(self, e):
        item = {
            "ambiente": self.txt_ambiente.value,
            "material": self.material_atual,
            "segmentos": self.segmentos,
            "recortes": self.recortes,
            "cuba": self.cuba,
            "area": float(self.lbl_area.value.split()[1]),
            "preco_total": float(
                self.lbl_total.value.replace("R$", "").replace(".", "").replace(",", ".")
            )
        }
        self.on_save_item(item)
