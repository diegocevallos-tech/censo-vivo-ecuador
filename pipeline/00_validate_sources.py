"""Compare official MANLOC CSV headers with the dictionary using DuckDB samples.

Requires locally extracted files. Reports schema only, never individual rows.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import duckdb
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "raw" / "1.3 BDD_CPV_2022_MANLOC_CSV"
DICTIONARY = ROOT / "data" / "raw" / "DICCIONARIO_BDD_MANLOC.xlsx"
OUTPUT = ROOT / "data" / "interim" / "fase0_schema.json"
TABLES = {
    "Vivienda": ("CPV_2022_Vivienda_Manloc.csv", "1. Vivienda"),
    "Hogar": ("CPV_2022_Hogar_Manloc.csv", "2. Hogar"),
    "Mortalidad": ("CPV_2022_Mortalidad_Manloc.csv", "3. Mortalidad"),
    "Emigración": ("CPV_2022_Emigracion_Manloc.csv", "4. Emigración"),
    "Población": ("CPV_2022_Poblacion_Manloc.csv", "5. Población"),
}


def main() -> None:
    book = openpyxl.load_workbook(DICTIONARY, read_only=True, data_only=True)
    connection = duckdb.connect()
    result = {}
    for table, (filename, sheet_name) in TABLES.items():
        path = SOURCE_DIR / filename
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            csv_headers = next(csv.reader(stream, delimiter=";"))
        dictionary_codes = [
            row[0].strip()
            for row in list(book[sheet_name].values)[11:]
            if isinstance(row[0], str) and isinstance(row[1], str)
        ]
        escaped_path = path.as_posix().replace("'", "''")
        source = (
            f"read_csv('{escaped_path}', delim=';', header=true, "
            "all_varchar=true, sample_size=1000)"
        )
        duckdb_headers = [
            row[0] for row in connection.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()
        ]
        sample_rows = connection.execute(
            f"SELECT COUNT(*) FROM (SELECT * FROM {source} LIMIT 100)"
        ).fetchone()[0]
        result[table] = {
            "filename": filename,
            "csv_columns": len(csv_headers),
            "dictionary_columns": len(dictionary_codes),
            "duckdb_columns": len(duckdb_headers),
            "sample_rows_read_by_duckdb": sample_rows,
            "csv_not_in_dictionary": sorted(set(csv_headers) - set(dictionary_codes)),
            "dictionary_not_in_csv": sorted(set(dictionary_codes) - set(csv_headers)),
            "csv_matches_duckdb": csv_headers == duckdb_headers,
        }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if any(
        item["csv_not_in_dictionary"]
        or item["dictionary_not_in_csv"]
        or not item["csv_matches_duckdb"]
        for item in result.values()
    ):
        raise SystemExit("Schema mismatch between official dictionary, CSV and DuckDB")


if __name__ == "__main__":
    main()
