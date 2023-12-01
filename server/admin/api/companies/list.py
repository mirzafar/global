from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.pager import Pager
from core.tools import set_counters
from utils.lists import ListUtils
from utils.strs import StrUtils


class CompaniesListView(BaseAPIView):

    async def get(self, request, user):
        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(request.args.get('limit', 20))
        query = StrUtils.to_str(request.args.get('query'))

        cond, cond_vars = ['status >= {}'], [0]
        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        companies = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM public.companies
            WHERE %s
            ORDER BY id DESC
            %s
            ''' % (cond, pager.as_query()),
            *cond_vars
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.companies
            WHERE status >= 0
            '''
        ) or 0

        return response.json({
            '_success': True,
            'companies': companies,
            'pager': pager.dict(),
            'user': dict(user),
        }, dumps=encoder.encode)
