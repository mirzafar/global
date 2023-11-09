from core.db import db
from core.handlers import BaseAPIView
from core.pager import Pager
from utils.lists import ListUtils


class UsersView(BaseAPIView):
    template_name = 'admin/users.html'

    async def get(self, request, user):
        self.user = user
        context = dict()
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 50)

        pager = Pager()
        pager.set_page(page)
        pager.set_limit(limit)

        users = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                u.*, 
                r.title AS role_title
            FROM public.users u
            LEFT JOIN public.roles r ON u.role_id = r.id
            WHERE u.status > -2
            ORDER BY id DESC
            %s
            ''' % pager.as_query()
        ))

        total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.users u
            WHERE u.status > -2
            '''
        ) or 0

        context['data'] = {
            'users': users,
            'total': total,
            'page': page,
            'limit': limit,
            'next_page': pager.next_page(total),
            'prev_page': pager.prev_page(),
        }

        return self.render_template(request=request, **context)
