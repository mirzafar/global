from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class TestingsAnswersAPIView(BaseAPIView):
    async def get(self, request, user, question_id):
        question_id = IntUtils.to_int(question_id)
        if not question_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): question_id'
            })

        answers = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT a.*
            FROM testings.answers a
            WHERE a.status >= 0 AND question_id = $1
            ORDER BY a.id DESC 
            ''',
            question_id
        ))

        return response.json({
            '_success': True,
            'answers': answers
        })

    async def post(self, request, user, question_id):
        question_id = IntUtils.to_int(question_id)
        if not question_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): question_id'
            })

        title = StrUtils.to_str(request.json.get('title'))
        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        answer = await db.fetchrow(
            '''
            INSERT INTO testings.answers(title, question_id)
            VALUES ($1, $2)
            RETURNING *
            ''',
            title,
            question_id
        )

        if not answer:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True,
            'answer': dict(answer)
        })
