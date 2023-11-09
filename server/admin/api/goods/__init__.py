from sanic import Blueprint

from .create import GoodCreateView
from .item import GoodItemView
from .list import GoodsView

__all__ = ['goods_bp']

goods_bp = Blueprint('goods')

goods_bp.add_route(GoodsView.as_view(), '/goods/', name='goods.list')
goods_bp.add_route(GoodCreateView.as_view(), '/good/create/', name='good.create')
goods_bp.add_route(GoodItemView.as_view(), '/good/<good_id>/', name='good.item')
