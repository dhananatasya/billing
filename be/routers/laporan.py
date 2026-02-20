from fastapi import APIRouter, Query
from crud import get_laporan

router = APIRouter()

@router.get("/")
def laporan(
    tgl_mulai: str = Query(None),
    tgl_akhir: str = Query(None)
):
    return get_laporan(tgl_mulai, tgl_akhir)