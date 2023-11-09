from sanic import Blueprint

from .list import ToolsView
from .rent.list import RentView
from .rent.create import RentCreateView
from .rent.item import RentItemView

__all__ = ['tools_bp']

tools_bp = Blueprint('tools', url_prefix='/tools')

tools_bp.add_route(ToolsView.as_view(), '/', name='tools.list')
tools_bp.add_route(RentView.as_view(), '/rent/', name='tools.rent.list')
tools_bp.add_route(RentCreateView.as_view(), '/rent/create/', name='tools.rent.create')
tools_bp.add_route(RentItemView.as_view(), '/rent/<rent_id>/', name='tools.rent.item')
