from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.pager import Pager
from core.tools import set_counters
from utils.lists import ListUtils
from utils.strs import StrUtils


class LessonsView(BaseAPIView):

    async def get(self, request, user):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 3)

        pager = Pager()
        pager.set_page(page)
        pager.set_limit(limit)

        query = StrUtils.to_str(request.args.get('query'))

        cond, cond_vars = ['l.status >= {}'], [0]

        if query:
            cond.append('l.title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))

        lessons = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                l.*
            FROM public.lessons l
            WHERE %s
            ORDER BY l.id DESC
            %s
            ''' % (cond, pager.as_query()),
            *cond_vars
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.lessons l
            WHERE l.status >= 0
            '''
        ) or 0

        self.context = {
            '_success': True,
            'lessons': lessons,
            'pager': pager.dict()
        }

        return response.json(self.context, dumps=encoder.encode)
