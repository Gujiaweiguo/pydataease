# pyright: reportMissingModuleSource=false
from __future__ import annotations

from pathlib import Path
from openpyxl import Workbook


def _normalize_row(row: object) -> list[object]:
    if isinstance(row, dict):
        return list(row.values())
    if isinstance(row, (list, tuple)):
        return list(row)
    return [row]

def generate_export_file(
    task_id: str,
    file_name: str | None,
    params: dict[str, object] | None,
    export_dir: str,
) -> tuple[str, int]:
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    base_name = (file_name or f"export-{task_id}").strip() or f"export-{task_id}"
    safe_name = Path(base_name).name
    if not safe_name.lower().endswith(".xlsx"):
        safe_name = f"{safe_name}.xlsx"

    workbook = Workbook()
    worksheet = workbook.active
    if worksheet is None:
        raise ValueError("Workbook active worksheet is unavailable")
    worksheet.title = "Export"

    rows = params.get("data") if isinstance(params, dict) else None
    if isinstance(rows, list) and rows:
        for row in rows:
            worksheet.append(_normalize_row(row))
    else:
        worksheet.append(["No data"])

    file_path = export_path / safe_name
    workbook.save(file_path)
    return str(file_path), file_path.stat().st_size
