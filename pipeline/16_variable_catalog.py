"""Generate the browser variable catalog from the verified INEC dictionaries.

The catalog contains metadata and category labels, never census records.
Availability follows the categories actually published in the exact aggregates.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import warnings
from pathlib import Path
from zipfile import ZipFile

import openpyxl
import pyarrow.parquet as pq
from category_counts import HIGH_CARDINALITY
from place_names import title_name

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
MANIFEST = ROOT / "data/MANIFEST.json"
CODEBOOK = ROOT / "data/interim/exact_public/counts/v1b1/categories/codebook.parquet"
OUTPUT = ROOT / "web/public/meta/variables.json"
ENGLISH = ROOT / "pipeline/variables_en.tsv"
DICTIONARIES = (
    ("DICCIONARIO_BDD_MANLOC.xlsx", "manzana"),
    ("DICCIONARIO_BDD_SECTOR.xlsx", "sector"),
    ("DICCIONARIO_BDD_CANTON.xlsx", "canton"),
)
TABLES = {"Vivienda": "vivienda", "Hogar": "hogar", "Población": "poblacion",
          "Emigración": "emigracion", "Mortalidad": "mortalidad"}
REFERENCE = {
    "vivienda": ("viviendas con respuesta", "responding dwellings"),
    "hogar": ("hogares con respuesta", "responding households"),
    "poblacion": ("personas con respuesta", "responding people"),
    "emigracion": ("emigrantes con respuesta", "responding emigrants"),
    "mortalidad": ("defunciones con respuesta", "reported deaths"),
}
EN_NAMES = {
    "V01": "Dwelling type", "V0201": "Private dwelling occupancy",
    "V0202": "Collective dwelling occupancy",
    "V03": "Roof material", "V04": "Roof condition", "V05": "Exterior wall material",
    "V06": "Exterior wall condition", "V07": "Floor material", "V08": "Floor condition",
    "V09": "Water supply", "V10": "Water source", "V11": "Sanitation service",
    "V12": "Grid electricity", "V13": "Other electricity source", "V14": "Waste disposal",
    "V15": "Number of rooms", "V16": "Shared food expenses", "V17": "Households in dwelling",
    "H01": "Bedrooms", "H02": "Separate cooking space", "H03": "Toilet availability",
    "H04": "Bathing facilities", "H05": "Cooking fuel", "H06": "Drinking water",
    "H0701": "Separates organic waste", "H0702": "Separates animal or plant waste",
    "H0703": "Separates recyclables", "H0801": "Household has dogs",
    "H0801N": "Number of dogs", "H0802": "Household has cats",
    "H0802N": "Number of cats", "H09": "Housing tenure",
    "H1001": "Landline telephone", "H1002": "Mobile telephone",
    "H1003": "Pay television", "H1004": "Fixed internet",
    "H1005": "Computer", "H1006": "Refrigerator", "H1007": "Washing machine",
    "H1008": "Clothes dryer", "H1009": "Microwave oven", "H1010": "Extractor hood",
    "H1011": "Car or pickup", "H1012": "Motorcycle",
    "H11": "Recent death in household", "H1101": "Number of deaths",
    "H12": "Emigration from household", "H1201": "Number of emigrants",
    "H1301": "Men in household", "H1302": "Women in household",
    "H1303": "Household members", "H15": "Unlisted household member",
    "M0201": "Death month", "M0202": "Death year", "M03": "Age at death",
    "M04": "Sex of deceased", "M05": "Maternal death", "M06": "Cause of death",
    "E01": "Departure year", "E02": "Emigrant sex", "E03": "Age at departure",
    "E04": "Current country of residence", "P01": "Relationship to household head",
    "P02": "Sex at birth", "P03": "Age", "P05": "Civil registration",
    "P0601": "Ecuadorian identity card", "P0602": "Other identity document",
    "P0701": "Difficulty walking", "P0702": "Difficulty with self care",
    "P0703": "Difficulty communicating", "P0704": "Difficulty hearing",
    "P0705": "Difficulty seeing", "P0706": "Difficulty remembering",
    "P08": "Place of birth", "P08P": "Birth province", "P08C": "Birth canton",
    "P08Q": "Birth parish", "P0803A": "Year of arrival in Ecuador",
    "P09": "Residence five years ago", "P09P": "Previous province",
    "P09C": "Previous canton", "P09Q": "Previous parish",
    "P1001": "Indigenous language", "P1002": "Spanish language",
    "P1003": "Foreign language", "P1004": "Ecuadorian sign language",
    "P1005": "Does not communicate", "P1001I": "Which Indigenous language",
    "P13": "Parent speaks Indigenous language", "P15": "School attendance",
    "P16": "School provider", "P17R": "Education level",
    "P18R": "Highest grade completed", "P19": "Literacy",
    "P20": "Educational qualification", "P2101": "Recent mobile phone use",
    "P2102": "Recent internet use", "P2103": "Recent computer use",
    "P2104": "Recent tablet use", "P22": "Activity last week",
    "P23": "Agricultural work", "P24": "Agricultural products",
    "P25": "Job search", "P26": "Reason not working",
    "P27": "Occupation", "P28": "Economic activity",
    "P29": "Employment status", "P30": "Social security contribution",
    "P31": "Marital status", "P3201": "Daughters ever born",
    "P3202": "Sons ever born", "P3203": "Children ever born",
    "P3301": "Daughters alive", "P3302": "Sons alive",
    "P3303": "Children alive", "P34": "Age at first birth",
    "P3501": "Day of last birth", "P3502": "Month of last birth",
    "P3503": "Year of last birth", "P10R": "Languages spoken",
    "P17_CINE": "Education level (ISCED)", "P11R": "Ethnic self identification",
    "H01R": "Bedroom count, recoded", "P0402": "Age in months",
    "P0403": "Age in days", "P11": "Ethnic self identification",
    "P1108": "Indigenous people or nationality", "P12": "Indigenous language",
    "P14": "Education programme", "P17": "Highest education level",
    "P18": "Highest grade completed", "P36": "Recent live birth",
    "P37": "Last birth survival", "V0201R": "Private dwelling occupancy, recoded",
    "V15R": "Number of rooms, recoded",
}
EN_CATEGORIES = {
    "sí": "Yes", "si": "Yes", "no": "No", "hombre": "Male",
    "mujer": "Female", "masculino": "Male", "femenino": "Female",
    "bueno": "Good", "regular": "Fair", "malo": "Poor",
    "se ignora": "Unknown", "no sabe": "Unknown",
    "urbana": "Urban", "rural": "Rural", "propia": "Owned",
    "arrendada": "Rented", "ninguno": "None", "otro": "Other",
}
CODE = re.compile(r"^[VHEMP][0-9][A-Z0-9_]*$")
CATEGORY = re.compile(r"^\s*([0-9]+)\s*[.)-]?\s+(.+)$")


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def checked_dictionary(filename: str) -> Path:
    path = RAW / filename
    sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
    expected = next((item["sha256"] for item in sources if item["filename"] == filename), None)
    if not expected or not path.is_file():
        raise FileNotFoundError(f"Verified INEC dictionary unavailable: {filename}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"INEC dictionary checksum mismatch: {filename}")
    return path


def category_labels(raw: object) -> dict[str, str]:
    result = {}
    for line in str(raw or "").splitlines():
        match = CATEGORY.match(line)
        if match:
            result[match.group(1)] = clean(match.group(2))
    return result


def theme_for(table: str, code: str) -> str:
    if table == "emigracion":
        return "Diáspora"
    if table == "mortalidad":
        return "Mortalidad"
    if table == "vivienda":
        return "Vivienda y servicios"
    if table == "hogar":
        if code.startswith("H10"):
            return "Conectividad y equipamiento"
        if code.startswith(("H11", "H12")):
            return "Movilidad y memoria familiar"
        return "Hogar"
    if code.startswith(("P15", "P16", "P17", "P18", "P19", "P20")):
        return "Educación"
    if code.startswith("P21"):
        return "Brecha digital"
    if code.startswith(("P22", "P23", "P24", "P25", "P26", "P27", "P28", "P29", "P30")):
        return "Trabajo"
    if code.startswith(("P31", "P32", "P33", "P34", "P35", "P36", "P37")):
        return "Fecundidad"
    if code.startswith(("P10", "P11", "P12", "P13")):
        return "Diversidad"
    if code.startswith(("P08", "P09")):
        return "Movilidad interna"
    return "Población"


def read_dictionaries() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for filename, minimum in DICTIONARIES:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Data Validation extension")
            book = openpyxl.load_workbook(checked_dictionary(filename), read_only=True,
                                          data_only=True)
        for sheet in book:
            table = next((value for title, value in TABLES.items() if title in sheet.title), None)
            if table is None:
                continue
            for row in sheet.values:
                code = clean(row[0])
                if not CODE.fullmatch(code) or code in {"P00", "E00", "M00"}:
                    continue
                old = found.get(code)
                if old and old["table"] != table:
                    raise ValueError(f"Variable code reused by two tables: {code}")
                if old and old["source_level"] == "manzana":
                    continue
                if old and old["source_level"] == "sector" and minimum == "canton":
                    continue
                found[code] = {
                    "id": code, "table": table,
                    "name": {"es": clean(row[1]), "en": EN_NAMES.get(code, code)},
                    "question": {"es": clean(row[2]),
                                 "en": EN_NAMES.get(code, code)},
                    "dictionary_categories": category_labels(row[3]),
                    "type": "numeric" if "Numérico" in clean(row[5]) else "categorical",
                    "source_level": minimum,
                }
    return found


def geographic_labels() -> dict[str, str]:
    archive = checked_dictionary("CLASIFICADOR_GEOGRAFICO_2022.zip")
    with ZipFile(archive) as zipped:
        members = [name for name in zipped.namelist() if name.lower().endswith(".xlsx")]
        if len(members) != 1:
            raise ValueError("Expected one INEC geographic coding workbook")
        workbook = openpyxl.load_workbook(io.BytesIO(zipped.read(members[0])),
                                          read_only=True, data_only=True)
    labels = {}
    for sheet, key_column, name_column, width in (
        ("PROVINCIAS", 1, 2, 2), ("CANTONES", 3, 4, 4),
        ("PARROQUIAS", 5, 6, 6),
    ):
        for row in workbook[sheet].values:
            if row[key_column] is not None and row[name_column] is not None:
                key = str(row[key_column]).zfill(width)
                if key.isdigit():
                    labels[key] = title_name(row[name_column])
    return labels


def build() -> dict:
    if not CODEBOOK.is_file():
        raise FileNotFoundError(CODEBOOK)
    found = read_dictionaries()
    places = geographic_labels()
    translated = dict(line.split("\t", 1) for line in ENGLISH.read_text(
        encoding="utf-8").splitlines() if line.strip())
    observed: dict[str, list[dict]] = {}
    for item in pq.read_table(CODEBOOK).to_pylist():
        code = item["variable"]
        table = item["source_table"].removesuffix("_sector")
        if code in found and found[code]["table"] == table:
            observed.setdefault(code, []).append(item)
    variables = []
    for code, item in sorted(found.items(), key=lambda pair: pair[0]):
        published = code in observed or code == "P03"
        min_level = "canton" if code in HIGH_CARDINALITY else (
            "sector" if item["source_level"] == "sector" else item["source_level"])
        if code == "P11R":
            min_level = "sector"
        category_rows = sorted(observed.get(code, []), key=lambda row: row["category_id"])
        categories = []
        for row in category_rows:
            category = str(row["category"] or "")
            label = item["dictionary_categories"].get(category, category)
            source = "diccionario INEC" if label != category else "código INEC"
            if code in {"P08P", "P08C", "P08Q", "P09P", "P09C", "P09Q"}:
                geographic = places.get(category)
                if geographic:
                    label = geographic
                    source = "clasificador geográfico INEC 2022"
            english = EN_CATEGORIES.get(label.casefold(), translated.get(label, label))
            categories.append({"id": row["category_id"], "code": category,
                               "label": {"es": label, "en": english}, "label_source": source})
        if code == "P03":
            categories = [
                {"id": index, "code": f"{start:02d}_{start + 4:02d}" if index < 20
                 else "100_120",
                 "label": {"es": f"{start}–{start + 4}" if index < 20 else "100–120",
                           "en": f"{start}–{start + 4}" if index < 20 else "100–120"},
                 "midpoint": start + 2 if index < 20 else 110}
                for index, start in enumerate((*range(0, 100, 5), 100))
            ]
        reference_es, reference_en = REFERENCE[item["table"]]
        if code == "P03":
            reference_es, reference_en = "personas con edad conocida", "people with known age"
        variables.append({
            "id": code, "table": item["table"], "theme": theme_for(item["table"], code),
            "name": item["name"],
            "question": item["question"], "type": item["type"],
            "universe": {"es": reference_es, "en": reference_en,
                         "denominator": "sum_valid_categories"},
            "min_level": min_level, "available": published,
            "delivery": "grouped_age" if code == "P03" else
                        "categories" if category_rows else "unavailable",
            "categories": categories,
        })
    result = {"source": "INEC CPV 2022 · diccionarios MANLOC/SECTOR/CANTON",
              "geom_version": "marco-2021", "variables": variables}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    summary = {"variables": len(variables), "available": sum(v["available"] for v in variables),
               "categories": sum(len(v["categories"]) for v in variables),
               "bytes": OUTPUT.stat().st_size}
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    build()
