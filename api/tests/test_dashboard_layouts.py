import pytest

from services.dashboard_layouts import DashboardLayoutStore, WIDGET_CATALOG


def test_dashboard_layout_accepts_pages_widgets_and_sizes():
    layout=DashboardLayoutStore.validate({"pages":[{"id":"operations","name":"Operações","widgets":[{"id":"health-1","type":"health","size":"small"},{"id":"risk-1","type":"risks","size":"large"}]}]})
    assert layout["pages"][0]["name"]=="Operações"
    assert [item["type"] for item in layout["pages"][0]["widgets"]]==["health","risks"]
    assert {"health","changes","domains","history","risks","patterns","devices"}<=set(WIDGET_CATALOG)


def test_dashboard_layout_rejects_executable_or_unknown_widgets():
    with pytest.raises(ValueError,match="não autorizado"):
        DashboardLayoutStore.validate({"pages":[{"id":"x","widgets":[{"id":"bad","type":"javascript","content":"alert(1)"}]}]})


def test_dashboard_layout_limits_pages_and_widgets():
    with pytest.raises(ValueError,match="10 páginas"):
        DashboardLayoutStore.validate({"pages":[{"id":str(index)} for index in range(11)]})
    with pytest.raises(ValueError,match="30 widgets"):
        DashboardLayoutStore.validate({"pages":[{"id":"x","widgets":[{"id":str(index),"type":"health"} for index in range(31)]}]})
