from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class TestingsQuestionsItemAPIView(BaseAPIView):

    async def post(self, request, user, question_id):
        question_id = IntUtils.to_int(question_id)
        if not question_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): question_id'
            })

        title = StrUtils.to_str(request.json.get('title'))
        description = StrUtils.to_str(request.json.get('description'))
        photo = StrUtils.to_str(request.json.get('photo'))
        audio = StrUtils.to_str(request.json.get('audio'))
        video_link = StrUtils.to_str(request.json.get('video_link'))

        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        question = await db.fetchrow(
            '''
            UPDATE testings.questions
            SET title = $2, description = $3, video_link = $4, audio = $5, photo = $6
            WHERE id = $1
            RETURNING *
            ''',
            question_id,
            title,
            description,
            video_link,
            audio,
            photo,
        )

        if not question:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True,
            'question': dict(question)
        })

    async def delete(self, request, user, question_id):
        question_id = IntUtils.to_int(question_id)
        if not question_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): question_id'
            })

        question = await db.fetchrow(
            '''
            UPDATE testings.questions
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            question_id
        )

        if not question:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True,
            'question': dict(question)
        })
