"""Genera el libro de Excel: Registros, Resumen (tablas) y Gráficos."""
from datetime import datetime
from io import BytesIO

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from PIL import Image

import config as C
import stats

AZUL = "1F4E78"
CLARO = "DDEBF7"
borde = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
ANCHOS = {
    "codigo": 12, "fecha": 17, "registrado_por": 18, "lugar": 28, "pelaje_predominante": 20,
    "pelaje_detalle": 28, "sexo": 14, "gestacion": 16, "estado_sanitario": 38,
    "estado_sanitario_detalle": 32, "edad": 14, "condicion_corporal": 16,
    "condicion_detalle": 24, "tamano": 18, "info_adicional": 45,
}


def _encabezado(celda):
    celda.font = Font(bold=True, color="FFFFFF")
    celda.fill = PatternFill("solid", fgColor=AZUL)
    celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    celda.border = borde


def _hoja_registros(wb, df, fotos):
    ws = wb.active
    ws.title = "Registros"
    cols = list(C.ETIQUETAS)
    headers = [C.ETIQUETAS[c] for c in cols] + (["Foto"] if fotos else [])
    ws.append(headers)
    for i in range(1, len(headers) + 1):
        _encabezado(ws.cell(row=1, column=i))
    ws.row_dimensions[1].height = 34

    df = df.sort_values("id") if len(df) else df
    for r, (_, fila) in enumerate(df.iterrows(), start=2):
        ws.append([("" if pd.isna(fila[c]) else fila[c]) for c in cols])
        for j in range(1, len(cols) + 1):
            c = ws.cell(row=r, column=j)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = borde
            if r % 2 == 1:
                c.fill = PatternFill("solid", fgColor="F2F2F2")
        if fotos and int(fila["id"]) in fotos:
            img = Image.open(BytesIO(fotos[int(fila["id"])])).convert("RGB")
            img.thumbnail((90, 90))
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            xl = XLImage(buf)
            xl.width, xl.height = img.size
            ws.add_image(xl, f"{get_column_letter(len(cols) + 1)}{r}")
            ws.row_dimensions[r].height = 72

    for i, c in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = ANCHOS[c]
    if fotos:
        ws.column_dimensions[get_column_letter(len(cols) + 1)].width = 16
    ws.freeze_panes = "B2"
    if len(df):
        ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(df) + 1}"


def _hoja_resumen(wb, df, tablas):
    ws = wb.create_sheet("Resumen")
    ws["A1"] = "Resumen de gatos registrados"
    ws["A1"].font = Font(bold=True, size=16, color=AZUL)
    ws["A3"], ws["B3"] = "Total de gatos registrados", len(df)
    ws["A4"], ws["B4"] = "Generado el", datetime.now().strftime("%Y-%m-%d %H:%M")
    ws["A3"].font = ws["B3"].font = Font(bold=True, size=13)
    ws["B3"].alignment = Alignment(horizontal="left")
    ws["B4"].alignment = Alignment(horizontal="left")

    refs = []
    fila = 6
    for titulo, t in tablas.items():
        ws.cell(row=fila, column=1, value=titulo).font = Font(bold=True, size=12, color=AZUL)
        fila += 1
        ws.cell(row=fila, column=1, value="Categoría")
        ws.cell(row=fila, column=2, value="Cantidad")
        _encabezado(ws.cell(row=fila, column=1))
        _encabezado(ws.cell(row=fila, column=2))
        cab = fila
        for _, r in t.iterrows():
            fila += 1
            a, b = ws.cell(row=fila, column=1, value=r["Categoría"]), ws.cell(row=fila, column=2, value=int(r["Cantidad"]))
            a.border = b.border = borde
        refs.append((titulo, cab, fila, len(t)))
        fila += 3
    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 18
    return ws, refs


def _hoja_graficos(wb, ws_res, refs, total):
    ws = wb.create_sheet("Gráficos")
    ws["A1"] = "Gráficos de gatos registrados"
    ws["A1"].font = Font(bold=True, size=16, color=AZUL)
    ws["A3"] = f"Total de gatos registrados: {total}"
    ws["A3"].font = Font(bold=True, size=14)

    graficados = [x for x in refs if x[3] > 0]
    for k, (titulo, cab, ult, _) in enumerate(graficados):
        es_pie = titulo.startswith("Sexo")
        ch = PieChart() if es_pie else BarChart()
        ch.title = titulo
        if not es_pie:
            ch.type = "col"
            ch.legend = None
            ch.y_axis.title = "Cantidad de gatos"
            ch.y_axis.majorUnit = 1
            ch.x_axis.delete = False
            ch.y_axis.delete = False
        data = Reference(ws_res, min_col=2, min_row=cab, max_row=ult)
        cats = Reference(ws_res, min_col=1, min_row=cab + 1, max_row=ult)
        ch.add_data(data, titles_from_data=True)
        ch.set_categories(cats)
        ch.dataLabels = DataLabelList()
        ch.dataLabels.showVal = not es_pie
        ch.dataLabels.showPercent = es_pie
        ch.dataLabels.showCatName = False
        ch.dataLabels.showSerName = False
        ch.dataLabels.showLegendKey = False
        ch.width, ch.height = 16, 8.5
        ancla = f"{'A' if k % 2 == 0 else 'L'}{5 + 19 * (k // 2)}"
        ws.add_chart(ch, ancla)


def construir_excel(df: pd.DataFrame, fotos: dict[int, bytes] | None = None) -> bytes:
    wb = Workbook()
    _hoja_registros(wb, df, fotos)
    ws_res, refs = _hoja_resumen(wb, df, stats.tablas(df))
    _hoja_graficos(wb, ws_res, refs, len(df))
    out = BytesIO()
    wb.save(out)
    return out.getvalue()
