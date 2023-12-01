from sanic import Blueprint

from admin.api.visits.item import VisitsItemView
from admin.api.visits.list import VisitsListView
from admin.api.visits.template import VisitsTemplateView, VisitsTemplateItemView

visits_bp = Blueprint('visits', url_prefix='/visits')

visits_bp.add_route(VisitsTemplateView.as_view(), '/template/')
visits_bp.add_route(VisitsListView.as_view(), '/list/')
visits_bp.add_route(VisitsItemView.as_view(), '/<visit_id>/item/')
visits_bp.add_route(VisitsTemplateItemView.as_view(), '/<visit_id>/item/template/')
