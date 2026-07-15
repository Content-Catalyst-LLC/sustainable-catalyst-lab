from app.visualization import build_spec, catalog, csv_text
from app.methods.numerical import monte_carlo_propagation


def test_catalog_profiles_and_formats():
    data=catalog(); assert data["version"]=="0.27.4"; assert len(data["profiles"])==8; assert data["formats"]==["svg","png","csv","json"]


def test_ode_time_series_spec():
    spec=build_spec({"method":"numerics.ode_first_order","outputs":{"time":[0,1,2],"values":[1,2,4]},"visualization":{"type":"auto"}})
    assert spec["kind"]=="line"; assert spec["series"][0]["points"][-1]=={"x":2.0,"y":4.0}; assert spec["accessibility"]["tabularFallback"] is True


def test_fft_spectrum_spec():
    spec=build_spec({"method":"signal.fft_spectrum","outputs":{"frequencyHz":[0,1,2],"amplitude":[0,2,1],"peakFrequencyHz":1}})
    assert spec["visualizationType"]=="spectrum"; assert spec["annotations"][0]["x"]==1


def test_uncertainty_histogram_and_csv():
    outputs=monte_carlo_propagation({"model":"product","samples":500,"distributions":[{"name":"a","distribution":"normal","mean":2,"stdDev":.1},{"name":"b","distribution":"normal","mean":4,"stdDev":.2}]},{"confidence":.95},42)
    spec=build_spec({"method":"uncertainty.monte_carlo_propagation","outputs":outputs})
    assert spec["kind"]=="histogram"; assert len(spec["bars"])>=8; assert "Lower bound" in csv_text(spec)


def test_sensitivity_tornado_spec():
    spec=build_spec({"method":"sensitivity.local_finite_difference","outputs":{"sensitivities":[{"variable":"x","derivative":2,"elasticity":1},{"variable":"y","derivative":-3,"elasticity":-.5}]}})
    assert spec["kind"]=="horizontal-bars"; assert spec["bars"][0]["label"]=="y"


def test_parameter_sweep_spec():
    spec=build_spec({"method":"simulation.parameter_sweep","outputs":{"parameter":"rate","model":"logistic","rows":[{"parameterValue":.1,"output":10},{"parameterValue":.2,"output":20}]}})
    assert spec["kind"]=="line"; assert spec["xLabel"]=="rate"


def test_convergence_spec():
    spec=build_spec({"method":"benchmark-convergence","outputs":{"rows":[{"level":1,"absoluteError":.1,"runtimeMs":1},{"level":2,"absoluteError":.01,"runtimeMs":2}]},"visualization":{"type":"convergence"}})
    assert spec["scale"]["y"]=="log"; assert spec["series"][0]["points"][1]["y"]==.01


def test_heatmap_spec():
    spec=build_spec({"method":"custom-grid","outputs":{"xValues":[0,1],"yValues":[0,1],"zMatrix":[[0,1],[1,2]]},"visualization":{"type":"heatmap"}})
    assert spec["kind"]=="heatmap"; assert len(spec["cells"])==4; assert spec["domain"]["z"]==[0.0,2.0]


def test_visualization_api_endpoints():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as client:
        health=client.get('/v1/visualization/health')
        assert health.status_code==200 and health.json()['version']=='0.27.4'
        profiles=client.get('/v1/visualization/profiles')
        assert profiles.status_code==200 and len(profiles.json()['profiles'])==8
        spec=client.post('/v1/visualization/spec',json={'method':'simulation.parameter_sweep','outputs':{'parameter':'rate','model':'logistic','rows':[{'parameterValue':.1,'output':10},{'parameterValue':.2,'output':20}]}})
        assert spec.status_code==200 and spec.json()['visualizationType']=='parameter-sweep'
        csv_response=client.post('/v1/visualization/csv',json={'method':'numerics.ode_first_order','outputs':{'time':[0,1],'values':[1,2]}})
        assert csv_response.status_code==200 and 'Time' in csv_response.json()['text']
