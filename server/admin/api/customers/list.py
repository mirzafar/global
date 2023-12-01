from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.pager import Pager
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class CustomersListView(BaseAPIView):

    async def get(self, request, user):
        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(request.args.get('limit', 20))

        query = StrUtils.to_str(request.args.get('query'))
        status = IntUtils.to_int(request.args.get('status'), default=0)

        cond, cond_vars = [], []
        if query:
            cond.append('(c.first_name ILIKE {} OR c.last_name ILIKE {})')
            cond_vars.append(f'%{query}%')
            cond_vars.append(f'%{query}%')

        if status is not None:
            cond.append('c.status = {}')
            cond_vars.append(status)

        cond, _ = set_counters(' AND '.join(cond))
        data = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT c.*
            FROM public.customers c
            WHERE %s
            ORDER BY c.id DESC
            %s
            ''' % (cond, pager.as_query()),
            *cond_vars
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.customers c
            WHERE %s
            ''' % cond,
            *cond_vars
        ) or 0

        return response.json({
            '_success': True,
            'data': data,
            'pager': pager.dict(),
            'user': dict(user),
        }, dumps=encoder.encode)
