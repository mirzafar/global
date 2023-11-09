from sanic import Blueprint

from .create import UsersCreateView
from .item import UsersItemView
from .list import UsersView

__all__ = ['users_bp']

users_bp = Blueprint('users')

users_bp.add_route(UsersCreateView.as_view(), '/users/create/', name='users.create')
users_bp.add_route(UsersView.as_view(), '/users/', name='users.list')
users_bp.add_route(UsersItemView.as_view(), '/users/<user_id>/', name='users.item')
