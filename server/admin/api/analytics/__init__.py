from sanic import Blueprint

from .expenses import ExpensesView
from .analytics import AnalyticsView

__all__ = ['analytics_bp']

analytics_bp = Blueprint('analytics', url_prefix='/analytics')

analytics_bp.add_route(ExpensesView.as_view(), '/expenses/', name='expenses')
analytics_bp.add_route(AnalyticsView.as_view(), '/', name='analytics')
