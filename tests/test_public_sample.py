"""Check the versioned canton sample against published official totals."""

from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "web/public/data/sample/canton.parquet"


def test_canton_sample_is_aggregate_and_complete() -> None:
    table = pq.read_table(SAMPLE)
    assert table.num_rows == 221
    assert set(table.column_names).isdisjoint(
        {"PERSONA_ID", "HOGAR_ID", "VIVIENDA_ID", "PERID", "HOGID", "VIVID"}
    )
    assert sum(table.column("population").to_pylist()) == 16_938_986
    assert sum(table.column("dwellings").to_pylist()) == 6_611_555
    assert SAMPLE.stat().st_size < 2_000_000
