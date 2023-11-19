from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from core.pager import Pager
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


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

        questions = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM testings.questions
            WHERE status >= 0 AND lesson_id = $1
            ORDER BY id DESC
            %s
            ''' % pager.as_query(),
            lesson_id,
        ))

        pager.total = await db.fetchval(
            '''
            SELECT count(*)
            FROM testings.questions
            WHERE status >= 0 AND lesson_id = $1
            ''',
            lesson_id,
        ) or 0

        return response.json({
            '_success': True,
            'questions': questions,
            'pager': pager.dict(),
        })