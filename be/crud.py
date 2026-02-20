# crud_report.py
from database import get_connection
from datetime import timedelta

def format_durasi(seconds):
    """Format detik ke HH:MM:SS"""
    if not seconds or seconds == 0:
        return ""
    return str(timedelta(seconds=int(seconds)))

def get_laporan(tgl_mulai=None, tgl_akhir=None):
    """
    Ambil laporan semua department dengan total biaya per jenis panggilan
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            dep.extcode AS ext,
            dep.extname AS nama_pemakai,
            dep.divisi AS departemen,
            COALESCE(SUM(TIME_TO_SEC(d.durasi)),0) AS call_durasi,
            COALESCE(SUM(CASE WHEN d.idd='IDD' THEN d.biaya ELSE 0 END),0) AS idd_cost,
            COALESCE(SUM(CASE WHEN d.idd='NDD' THEN d.biaya ELSE 0 END),0) AS ndd_cost,
            COALESCE(SUM(CASE WHEN d.idd='CELL' THEN d.biaya ELSE 0 END),0) AS cell_cost,
            COALESCE(SUM(CASE WHEN d.idd='LDD' THEN d.biaya ELSE 0 END),0) AS ldd_cost,
            COALESCE(SUM(d.biaya),0) AS total_cost,
            MAX(TIMESTAMP(d.tglinsert, d.jammasuk)) AS last_call
        FROM tbm_department dep
        LEFT JOIN tbm_data_masuk d
            ON d.ext_pemanggil = dep.extcode
            AND (%s IS NULL OR d.tglinsert >= %s)
            AND (%s IS NULL OR d.tglinsert <= %s)
        GROUP BY dep.extcode, dep.extname, dep.divisi
        ORDER BY dep.extcode
    """

    params = [tgl_mulai, tgl_mulai, tgl_akhir, tgl_akhir]
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    total_all = {
        "no": "",
        "ext": "TOTAL",
        "nama_pemakai": "",
        "departemen": "",
        "call_durasi": 0,
        "idd_cost": 0,
        "ndd_cost": 0,
        "cell_cost": 0,
        "ldd_cost": 0,
        "total_cost": 0,
        "last_call": ""
    }

    for i, row in enumerate(rows, start=1):
        total_all["call_durasi"] += row["call_durasi"]
        total_all["idd_cost"] += float(row["idd_cost"])
        total_all["ndd_cost"] += float(row["ndd_cost"])
        total_all["cell_cost"] += float(row["cell_cost"])
        total_all["ldd_cost"] += float(row["ldd_cost"])
        total_all["total_cost"] += float(row["total_cost"])

        result.append({
            "no": i,
            "ext": row["ext"],
            "nama_pemakai": row["nama_pemakai"],
            "departemen": row["departemen"],
            "call_durasi": format_durasi(row["call_durasi"]),
            "idd_cost": float(row["idd_cost"]),
            "ndd_cost": float(row["ndd_cost"]),
            "cell_cost": float(row["cell_cost"]),
            "ldd_cost": float(row["ldd_cost"]),
            "total_cost": float(row["total_cost"]),
            "last_call": row["last_call"] if row["last_call"] else ""
        })

    # Format total
    total_all["call_durasi"] = format_durasi(total_all["call_durasi"])
    result.append(total_all)

    return result

# ====================================
# Contoh penggunaan
# ====================================
if __name__ == "__main__":
    laporan = get_laporan()  # tanpa tanggal = ambil semua
    print(f"{'No':<3} {'Ext':<5} {'Nama Pemakai':<20} {'Departemen':<15} {'Call Durasi':<10} {'IDD':<8} {'NDD':<8} {'CELL':<8} {'LDD':<8} {'Total':<10} {'Last Call':<20}")
    for row in laporan:
        print(f"{row['no']:<3} {row['ext']:<5} {row['nama_pemakai']:<20} {row['departemen']:<15} {row['call_durasi']:<10} {row['idd_cost']:<8} {row['ndd_cost']:<8} {row['cell_cost']:<8} {row['ldd_cost']:<8} {row['total_cost']:<10} {row['last_call']:<20}")