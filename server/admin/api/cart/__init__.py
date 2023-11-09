from sanic import Blueprint

from .story import StoryView
from .cart import CartView
from .item import CartItemView
from .checkout import CheckoutView
from .approve import ApproveView

__all__ = ['story_bp']

story_bp = Blueprint('story')

story_bp.add_route(CartView.as_view(), '/cart/', name='cart')
story_bp.add_route(ApproveView.as_view(), '/cart/approve/', name='cart.approve')
story_bp.add_route(CheckoutView.as_view(), '/checkout/', name='checkout')
story_bp.add_route(CartItemView.as_view(), '/cart/item/', name='cart.item')
