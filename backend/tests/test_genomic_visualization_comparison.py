from app.genomic_visualization_comparison import contract,execute
def test_benchmarks():
 c=contract();assert len(c["modes"])==8 and len(c["analysisMethods"])==8 and len(c["benchmarks"])==8
 for b in c["benchmarks"]:assert execute(b["methodId"],b["inputs"])["value"]==b["expected"]
