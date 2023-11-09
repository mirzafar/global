from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class LessonsItemView(BaseAPIView):
    template_name = 'admin/lessons-item.html'

    async def get(self, request, user, lesson_id):
        lesson_id = IntUtils.to_int(lesson_id)
        if not lesson_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): lesson_id'
            })

        lesson = await db.fetchrow(
            '''
            SELECT *
            FROM public.lessons
            WHERE id = $1
            ''',
            lesson_id
        )

        categories = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM public.categories
            WHERE status >= 0
            '''
        ))

        self.context['data'] = {
            'lesson': dict(lesson or {}),
            'categories': categories
        }

        return self.render_template(
            request=request,
            user=user
        )

    async def post(self, request, user, lesson_id):
        title = StrUtils.to_str(request.json.get('title'))
        description = StrUtils.to_str(request.json.get('description'))
        category_id = IntUtils.to_int(request.json.get('category_id'))
        logo = StrUtils.to_str(request.json.get('logo'))
        link = StrUtils.to_str(request.json.get('link'))

        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        lesson = await db.fetchrow(
            '''
            INSERT INTO public.lessons
            (title, description, category_id, logo, link)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            ''',
            title,
            description,
            category_id,
            logo,
            link,
        )

        if not lesson:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })

    async def put(self, request, user, lesson_id):
        lesson_id = IntUtils.to_int(lesson_id)
        if not lesson_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): user_id'
            })

        title = StrUtils.to_str(request.json.get('title'))
        description = StrUtils.to_str(request.json.get('description'))
        category_id = IntUtils.to_int(request.json.get('category_id'))
        logo = StrUtils.to_str(request.json.get('logo'))
        link = StrUtils.to_str(request.json.get('link'))

        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        lesson = await db.fetchrow(
            '''
            UPDATE public.lessons
            SET title = $2, description = $3, category_id = $4, logo = $5, link = $6
            WHERE id = $1
            RETURNING *
            ''',
            lesson_id,
            title,
            description,
            category_id,
            logo,
            link,
        )

        if not lesson:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })

    async def delete(self, request, user, lesson_id):
        lesson_id = IntUtils.to_int(lesson_id)
        if not lesson_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): lesson_id'
            })

        lesson = await db.fetchrow(
            '''
            UPDATE public.lessons
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            lesson_id
        )

        if not lesson:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })
