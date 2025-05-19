# riport_generator.py

from fpdf import FPDF
import os
from datetime import datetime

def riport_mentese(osszes_ertek, erme_szamlalok, futasi_ido, output_path='exports/riport.pdf'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.set_title("Ermefelismeresi Riport")

    pdf.cell(200, 10, txt="Ermefelismeresi Riport", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Dátum: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Feldolgozasi ido: {futasi_ido:.2f} mp", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Osszes ertek: {osszes_ertek} Ft", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Ermetipusok:", ln=True)
    for nev, db in erme_szamlalok.items():
        pdf.cell(200, 10, txt=f"- {nev}: {db} db", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt="A riport automatikusan generálódott és archiválási célra alkalmas.")

    pdf.output(output_path)
    return output_path
