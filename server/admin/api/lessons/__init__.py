from sanic import Blueprint

from .create import LessonsCreateView
from .item import LessonsItemView
from .list import LessonsView

__all__ = ['lessons_bp']

from .tags import LessonsTagsView, LessonsTagsItemView

lessons_bp = Blueprint('lessons', url_prefix='/lessons')

# Lessons
lessons_bp.add_route(LessonsCreateView.as_view(), '/create/', name='lessons.create')
lessons_bp.add_route(LessonsView.as_view(), '/', name='lessons.list')
lessons_bp.add_route(LessonsItemView.as_view(), '/<lesson_id>/', name='lessons.item')

# Tags
lessons_bp.add_route(LessonsTagsView.as_view(), '/tags/', name='lessons.tags.list')
lessons_bp.add_route(LessonsTagsItemView.as_view(), '/tags/<tag_id>/', name='lessons.tags.item')
