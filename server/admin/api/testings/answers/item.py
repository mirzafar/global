from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class TestingsAnswersItemAPIView(BaseAPIView):
    async def post(self, request, user, answer_id):
        answer_id = IntUtils.to_int(answer_id)
        if not answer_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): answer_id'
            })

        title = StrUtils.to_str(request.json.get('title'))
        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        answer = await db.fetchrow(
            '''
            UPDATE testings.answers
            SET title = $2
            WHERE id = $1
            RETURNING *
            ''',
            answer_id,
            title,
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

    async def delete(self, request, user, answer_id):
        answer_id = IntUtils.to_int(answer_id)
        if not answer_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): answer_id'
            })

        answer = await db.fetchrow(
            '''
            UPDATE testings.answers
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            answer_id,
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
