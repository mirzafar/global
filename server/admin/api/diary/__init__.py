from sanic import Blueprint

from .list import DiaryView
from .create import DiaryCreateView
from .item import DiaryItemView

__all__ = ['diary_bp']

diary_bp = Blueprint('diary')

diary_bp.add_route(DiaryView.as_view(), '/diary/', name='diary.list')
diary_bp.add_route(DiaryCreateView.as_view(), '/diary/create/', name='diary.create')
diary_bp.add_route(DiaryItemView.as_view(), '/diary/<diary_id>/', name='diary.item')
