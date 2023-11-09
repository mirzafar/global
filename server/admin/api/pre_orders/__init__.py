from sanic import Blueprint

from .create import PreOrderCreateView
from .item import PreOrdersItemView
from .list import PreOrdersView

__all__ = ['pre_orders_bp']

from .task.create import PreOrderTaskCreateView
from .task.item import PreOrdersTasksItemView
from .task.list import PreOrdersTasksView

pre_orders_bp = Blueprint('pre_orders')

pre_orders_bp.add_route(PreOrderTaskCreateView.as_view(), '/pre_orders/task/create/', name='pre.orders.task.create')
pre_orders_bp.add_route(PreOrdersTasksView.as_view(), '/pre_orders/task/list/', name='pre.orders.task.list')
pre_orders_bp.add_route(PreOrdersTasksItemView.as_view(), '/pre_orders/task/<item_id>/', name='pre.orders.task.item')

pre_orders_bp.add_route(PreOrderCreateView.as_view(), '/pre_orders/create/', name='pre.orders.create')
pre_orders_bp.add_route(PreOrdersView.as_view(), '/pre_orders/list/', name='pre.orders.list')
pre_orders_bp.add_route(PreOrdersItemView.as_view(), '/pre_orders/<item_id>/', name='pre.orders.item')
