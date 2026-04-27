import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{process_id}/executive-pdf")
def executive_pdf(process_id: int):
    file_path = f"report_process_{process_id}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Relatório Executivo do Processo {process_id}")

    c.setFont("Helvetica", 11)
    c.drawString(50, 770, "Resumo executivo")
    c.drawString(50, 750, "- principais gargalos")
    c.drawString(50, 735, "- desperdícios Lean")
    c.drawString(50, 720, "- sugestões To Be")
    c.save()

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Falha ao gerar PDF")

    return FileResponse(file_path, media_type="application/pdf", filename=file_path)
