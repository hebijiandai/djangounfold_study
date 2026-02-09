from unfold.sites import UnfoldAdminSite
from unfold.decorators import display
from unfold.widgets import (
    Kpi,
    Component,
)
from .models import Location, Faction, Creature, Consumable, Region

def dashboard_callback(request, context):
    """
    Callback to generate dashboard components.
    """
    return [
        Component(
            title="数据统计",
            template="unfold/dashboard/components/grid.html",
            children=[
                Kpi(
                    title="总地点数",
                    value=Location.objects.count(),
                    icon="location_on",
                ),
                Kpi(
                    title="总派系数",
                    value=Faction.objects.count(),
                    icon="group",
                ),
                Kpi(
                    title="总生物数",
                    value=Creature.objects.count(),
                    icon="bug_report",
                ),
            ],
            width=2,
        ),
        Component(
            title="更多统计",
            template="unfold/dashboard/components/grid.html",
            children=[
                Kpi(
                    title="总消耗品数",
                    value=Consumable.objects.count(),
                    icon="local_drink",
                ),
                Kpi(
                    title="总区域数",
                    value=Region.objects.count(),
                    icon="map",
                ),
            ],
            width=1,
        ),
    ]
