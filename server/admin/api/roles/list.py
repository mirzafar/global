from core.db import db
from core.handlers import BaseAPIView
from utils.lists import ListUtils


class RolesView(BaseAPIView):
    template_name = 'admin/roles.html'

    async def get(self, request, user):
        self.user = user
        context = dict()

        roles = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM public.roles
            WHERE status >= 0
            ORDER BY id DESC
            '''
        ))

        total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.roles
            WHERE status >= 0
            '''
        ) or 0

        context['data'] = {
            'roles': roles,
            'total': total
        }

        return self.render_template(request=request, **context)
