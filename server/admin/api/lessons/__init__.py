from sanic import Blueprint

from .create import LessonsCreateView
from .item import LessonsItemView
from .list import LessonsView

__all__ = ['lessons_bp']

lessons_bp = Blueprint('lessons', url_prefix='/lessons')

lessons_bp.add_route(LessonsCreateView.as_view(), '/create/', name='lessons.create')
lessons_bp.add_route(LessonsView.as_view(), '/', name='lessons.list')
lessons_bp.add_route(LessonsItemView.as_view(), '/<lesson_id>/', name='lessons.item')
