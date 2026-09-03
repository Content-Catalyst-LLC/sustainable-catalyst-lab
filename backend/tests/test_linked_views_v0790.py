from app.linked_views_v0790 import *

def test_health_and_boundaries():
    h=health(); assert h["status"]=="linked-views-faceting-composition-ready"; assert h["engineVersion"]=="2.6.0"; assert h["automaticLinkInference"] is False

def test_composition_preserves_mixed_renderers_and_explicit_links():
    c=normalize_composition({"title":"Mixed","views":[{"id":"a","renderer":"svg2d","figureKind":"scatter"},{"id":"b","renderer":"canvas3d","figureKind":"point-cloud-3d"},{"id":"c","renderer":"canvas4d","figureKind":"surface-4d"}],"links":[{"sourceViewId":"a","targetViewIds":["b","c"],"channel":"selection","key":"sample_id","direction":"bidirectional"}]})
    assert [v["renderer"] for v in c["views"]]==["svg2d","canvas3d","canvas4d"]
    assert c["boundaries"]["crossDatasetJoin"] is False

def test_link_event_is_declared_only():
    comp={"views":[{"id":"a"},{"id":"b"},{"id":"c"}],"links":[{"sourceViewId":"a","targetViewIds":["b"],"channel":"selection","key":"id"}]}
    r=apply_link_event({"composition":comp,"event":{"sourceViewId":"a","channel":"selection","value":["x"]}}); assert r["propagationCount"]==1; assert r["updates"][0]["viewId"]=="b"

def test_faceting_returns_source_row_indexes_without_copying_rows():
    d={"id":"d","rows":[{"group":"B","x":1},{"group":"A","x":2},{"group":"B","x":3},{"group":"A","x":4}]}
    r=facet_dataset({"dataset":d,"facet":{"field":"group","order":"ascending","columns":2}}); assert r["facetCount"]==2; assert r["facets"][0]["label"]=="A"; assert r["facets"][0]["rowIndexes"]==[1,3]; assert "rows" not in r["facets"][0]

def test_filter_links_require_key():
    import pytest
    with pytest.raises(LinkedViewsError): normalize_link({"sourceViewId":"a","targetViewIds":["b"],"channel":"filter"})

def test_workspace_with_facets():
    w=build_workspace({"composition":{"views":[{"id":"a"}]},"dataset":{"rows":[{"g":"x"},{"g":"y"}]},"facet":{"field":"g"}})["workspace"]; assert w["schema"]=="sc-lab-figure-workspace/0.79.0"; assert w["facetResult"]["facetCount"]==2
