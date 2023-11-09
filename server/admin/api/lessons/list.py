from core.db import db
from core.handlers import BaseAPIView
from core.pager import Pager
from utils.lists import ListUtils


class LessonsView(BaseAPIView):
    template_name = 'admin/lessons.html'

    async def get(self, request, user):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 50)

        pager = Pager()
        pager.set_page(page)
        pager.set_limit(limit)

        lessons = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                l.*
            FROM public.lessons l
            WHERE l.status >= 0
            ORDER BY l.id DESC
            %s
            ''' % pager.as_query()
        ))

        total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.lessons l
            WHERE l.status >= 0
            '''
        ) or 0

        self.context['data'] = {
            'lessons': lessons,
            'total': total,
            'page': page,
            'limit': limit,
            'next_page': pager.next_page(total),
            'prev_page': pager.prev_page(),
        }

        return self.render_template(
            request=request,
            user=user
        )
