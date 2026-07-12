from pathlib import Path


def test_render_blueprint_and_docker_markers() -> None:
    root = Path(__file__).resolve().parents[2]
    blueprint = (root / "render.yaml").read_text()
    dockerfile = (root / "backend" / "Dockerfile").read_text()
    assert "type: web" in blueprint
    assert "type: worker" in blueprint
    assert "type: keyvalue" in blueprint
    assert "healthCheckPath: /health" in blueprint
    assert "property: connectionString" in blueprint
    for runtime in ("gfortran", "golang-go", "rustc", "nodejs", "typescript"):
        assert runtime in dockerfile
    assert "USER sccompute" in dockerfile
