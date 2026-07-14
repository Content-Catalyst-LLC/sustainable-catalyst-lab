from app.genomics_production_health import genomics_production_health
def test_ready():
 h=genomics_production_health();assert h["ok"] and h["release"]=="0.24.1" and h["methodCount"]==48 and h["benchmarkCount"]==48 and h["categoryCount"]==8 and h["clinicalUse"] is False
