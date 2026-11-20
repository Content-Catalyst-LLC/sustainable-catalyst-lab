"""Run with PYTHONPATH=backend python backend/scripts/import_epa_soil_carbon.py PDF OUTPUT."""
import json
from pathlib import Path
import sys
from app.publisher_soil_carbon import ingest_pdf
if __name__ == '__main__':
    if len(sys.argv) != 3: raise SystemExit('Expected publisher PDF path and output JSON path')
    result = ingest_pdf(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
