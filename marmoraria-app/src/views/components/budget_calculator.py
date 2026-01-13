import flet as ft
from fpdf import FPDF
import math
import os
from src.services import firebase_service


class BudgetCalculator(ft.Column):
    def __init__(self, page: ft.Page, on_save_item, on_cancel):
        super().__init__(spacing=15)
        self.page = page
        self.on_save_item = on_save_item
        self.on_cancel = on_cancel

        # =========================
        # CAMPOS
        # =========================
        self.tipo = ft.Dropdown(
            label="Tipo da bancada",
            options=[
                ft.dropdown.Option("Reta"),
                ft.dropdown.Option("L"),
                ft.dropdown.Option("U"),
            ],
            value="Reta",
            filled=True
        )

        self.material = ft.Dropdown(label="Material", filled=True)
        self._carregar_materiais()

        self.comp_a = ft.TextField(label="Comprimento A (m)", keyboard_type=ft.KeyboardType.NUMBER)
        self.comp_b = ft.TextField(label="Comprimento B (m)", keyboard_type=ft.KeyboardType.NUMBER)
        self.comp_c = ft.TextField(label="Comprimento C (m)", keyboard_type=ft.KeyboardType.NUMBER)

        self.profundidade = ft.TextField(label="Profundidade (m)", value="0.60")

        self.saia = ft.TextField(label="Saia (m)", value="0")
        self.rodabanca = ft.TextField(label="Rodabanca (m)", value="0")

        self.txt_resultado = ft.Text(size=14, weight="bold")

        self.btn_pdf = ft.ElevatedButton(
            "Gerar PDF Técnico",
            icon=ft.icons.PICTURE_AS_PDF,
            on_click=self.gerar_pdf
        )

        self.btn_salvar = ft.ElevatedButton(
            "Salvar no orçamento",
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            on_click=self.salvar
        )

        self.controls = [
            ft.Text("Cálculo de Bancada", size=22, weight="bold"),
            self.tipo,
            self.material,
            self.comp_a,
            self.comp_b,
            self.comp_c,
            self.profundidade,
            ft.Row([self.saia, self.rodabanca]),
            self.txt_resultado,
            ft.Row([
                ft.TextButton("Cancelar", on_click=self.on_cancel),
                self.btn_pdf,
                self.btn_salvar
            ])
        ]

    # =========================
    # DADOS
    # =========================
    def _carregar_materiais(self):
        estoque = firebase_service.get_collection("estoque")
        self.materiais = {i["nome"]: i for i in estoque if "preco_m2" in i}

        self.material.options = [
            ft.dropdown.Option(k) for k in self.materiais.keys()
        ]

    # =========================
    # CÁLCULOS
    # =========================
    def calcular_area(self):
        try:
            a = float(self.comp_a.value or 0)
            b = float(self.comp_b.value or 0)
            c = float(self.comp_c.value or 0)
            prof = float(self.profundidade.value)

            if self.tipo.value == "Reta":
                return a * prof

            if self.tipo.value == "L":
                return (a + b) * prof

            if self.tipo.value == "U":
                return (a + b + c) * prof

        except:
            return 0

    def calcular_total(self):
        area = self.calcular_area()
        material = self.materiais.get(self.material.value)

        if not material:
            return 0

        preco_m2 = material.get("preco_m2", 0)
        return area * preco_m2

    # =========================
    # PDF
    # =========================
    def gerar_pdf(self, e):
        area = self.calcular_area()
        total = self.calcular_total()

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Projeto Técnico de Bancada", ln=True)

        pdf.ln(5)
        pdf.set_font("Helvetica", size=11)

        pdf.cell(0, 8, f"Tipo: {self.tipo.value}", ln=True)
        pdf.cell(0, 8, f"Material: {self.material.value}", ln=True)
        pdf.cell(0, 8, f"Área total: {area:.2f} m²", ln=True)
        pdf.cell(0, 8, f"Valor total: R$ {total:.2f}", ln=True)

        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Medidas:", ln=True)

        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, f"Comprimento A: {self.comp_a.value} m", ln=True)

        if self.tipo.value in ["L", "U"]:
            pdf.cell(0, 6, f"Comprimento B: {self.comp_b.value} m", ln=True)

        if self.tipo.value == "U":
            pdf.cell(0, 6, f"Comprimento C: {self.comp_c.value} m", ln=True)

        pdf.cell(0, 6, f"Profundidade: {self.profundidade.value} m", ln=True)
        pdf.cell(0, 6, f"Saia: {self.saia.value} m", ln=True)
        pdf.cell(0, 6, f"Rodabanca: {self.rodabanca.value} m", ln=True)

        path = "/tmp/projeto_bancada.pdf"
        pdf.output(path)

        self.page.snack_bar = ft.SnackBar(
            ft.Text("PDF técnico gerado com sucesso!")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # =========================
    # SALVAR
    # =========================
    def salvar(self, e):
        item = {
            "tipo": self.tipo.value,
            "material": self.material.value,
            "area": self.calcular_area(),
            "total": self.calcular_total(),
            "saia": float(self.saia.value or 0),
            "rodabanca": float(self.rodabanca.value or 0)
        }
        self.on_save_item(item)
