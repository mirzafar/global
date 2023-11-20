from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.pager import Pager
from utils.ints import IntUtils
from utils.lists import ListUtils


class TestingsResultsAPIView(BaseAPIView):
    async def get(self, request, user, lesson_id):
        lesson_id = IntUtils.to_int(lesson_id)
        if not lesson_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): lesson_id'
            })

        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)

        pager = Pager()
        pager.set_page(page)
        pager.set_limit(limit)

        cond, cond_vars = [], []

        results = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT r.*, u.username, u.last_name, u.first_name
            FROM testings.results r
            LEFT JOIN public.users u ON r.user_id = u.id
            WHERE r.lesson_id = $1
            ORDER BY r.id DESC
            %s
            ''' % pager.as_query(),
            lesson_id,
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM testings.results
            WHERE status >= 0 AND lesson_id = $1
            ''',
            lesson_id,
        ) or 0

        return response.json({
            '_success': True,
            'results': results,
            'pager': pager.dict(),
        }, dumps=encoder.encode)
