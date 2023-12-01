from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.pager import Pager
from core.tools import set_counters
from utils.lists import ListUtils
from utils.strs import StrUtils


class VisitsListView(BaseAPIView):

    async def get(self, request, user):
        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(request.args.get('limit', 20))
        query = StrUtils.to_str(request.args.get('query'))

        cond, cond_vars = ['v.status >= {}'], [0]
        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        visits = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                v.*,
                (
                    CASE WHEN cu.id IS NULL THEN NULL ELSE
                    jsonb_build_object(
                        'id', cu.id,
                        'last_name', cu.last_name,
                        'first_name', cu.first_name
                    )
                    END
                ) AS customer,
                (
                    CASE WHEN u.id IS NULL THEN NULL ELSE
                    jsonb_build_object(
                        'id', u.id,
                        'last_name', u.last_name,
                        'first_name', u.first_name
                    )
                    END
                ) AS "user",
                (
                    CASE WHEN ct.id IS NULL THEN NULL ELSE
                    jsonb_build_object(
                        'id', ct.id,
                        'title', ct.title
                    )
                    END
                ) AS category
            FROM public.visits v
            LEFT JOIN public.customers cu ON v.customer_id = cu.id
            LEFT JOIN public.users u ON v.user_id = u.id
            LEFT JOIN public.categories ct ON v.category_id = ct.id
            WHERE %s
            ORDER BY v.id DESC
            %s
            ''' % (cond, pager.as_query()),
            *cond_vars
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM public.visits v
            WHERE status >= 0
            '''
        ) or 0

        return response.json({
            '_success': True,
            'visits': visits,
            'pager': pager.dict(),
            'user': dict(user),
        }, dumps=encoder.encode)
