from sanic import response

from core.db import db
from core.handlers import BaseAPIView
from utils.floats import FloatUtils
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

        lesson = dict(lesson or {})

        if lesson.get('discount') and 1 < lesson['discount'] < 100 and lesson.get('price'):
            lesson['price'] = lesson['price'] * 100 / (100 - lesson['discount'])

        categories = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM public.categories
            WHERE status >= 0
            '''
        ))

        tags = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM public.tags
            WHERE status >= 0
            '''
        ))

        self.context = {
            'lesson': lesson,
            'categories': categories,
            'tags': tags,
        }

        return self.render_template(
            request=request,
            user=user
        )

    async def post(self, request, user, lesson_id):
        action = StrUtils.to_str(request.json.get('action'), default='create')
        if action == 'create':
            title = StrUtils.to_str(request.json.get('title'))
            description = StrUtils.to_str(request.json.get('description'))
            category_id = IntUtils.to_int(request.json.get('category_id'))
            logo = StrUtils.to_str(request.json.get('logo'))
            link = StrUtils.to_str(request.json.get('link'))
            price = FloatUtils.to_float(request.json.get('price'), default=0.0)
            discount = IntUtils.to_int(request.json.get('discount'), default=0)
            tag_ids = ListUtils.to_list_of_ints(request.json.get('tag_ids'))

            if not title:
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): title'
                })

            if discount and 1 < discount < 100:
                price = price * (100 - discount) / 100

            lesson = await db.fetchrow(
                '''
                INSERT INTO public.lessons
                (title, description, category_id, logo, link, price, discount, tag_ids)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
                ''',
                title,
                description,
                category_id,
                logo,
                link,
                price,
                discount,
                tag_ids,
            )

            if not lesson:
                return response.json({
                    '_success': False,
                    'message': 'Operation failed'
                })

            return response.json({
                '_success': True
            })

        elif action == 'subscribe':
            lesson_id = IntUtils.to_int(lesson_id)
            if not lesson_id:
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): user_id'
                })

            await db.fetchrow(
                '''
                UPDATE public.lessons
                SET subscribers = array_append(COALESCE(subscribers, ARRAY[]::integer[]), $2)
                WHERE id = $1 AND $2 != ALL (subscribers)
                RETURNING *
                ''',
                lesson_id,
                user['id'],
            )

        elif action == 'unsubscribe':
            lesson_id = IntUtils.to_int(lesson_id)
            if not lesson_id:
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): user_id'
                })

            await db.fetchrow(
                '''
                UPDATE public.lessons
                SET subscribers = array_remove(COALESCE(subscribers, ARRAY[]::integer[]), $2)
                WHERE id = $1 AND $2 = ALL (subscribers)
                RETURNING *
                ''',
                lesson_id,
                user['id'],
            )

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
        price = FloatUtils.to_float(request.json.get('price'), default=0.0)
        discount = IntUtils.to_int(request.json.get('discount'), default=0)
        tag_ids = ListUtils.to_list_of_ints(request.json.get('tag_ids'))
        testing_state = IntUtils.to_int(request.json.get('testing_state'))
        testing_count = IntUtils.to_int(request.json.get('testing_count'))

        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        if testing_state == 1:
            questions = await db.fetchrow(
                '''
                SELECT
                    array_agg(id) AS question_ids,
                    count(id) FILTER ( WHERE current_answer_id IS NULL ) AS count
                FROM testings.questions
                WHERE lesson_id = $1 AND status >= 0
                ''',
                lesson_id
            )
            question_ids = questions['question_ids']
            question_count = questions['count']

            if question_ids:
                ids = await db.fetchval(
                    '''
                    SELECT array_agg(DISTINCT question_id)
                    FROM testings.answers
                    WHERE status >= 0 AND question_id = ANY ($1)
                    ''',
                    question_ids
                )
                for x in question_ids:
                    if x not in list(ids or []):
                        return response.json({
                            '_success': False,
                            'message': 'Ответы на вопросы не найден'
                        })

            else:
                return response.json({
                    '_success': False,
                    'message': 'Вопросы для тестирования не найдены'
                })

            if question_count:
                return response.json({
                    '_success': False,
                    'message': 'У вопроса отсутствует правильный ответ'
                })

        if discount and 1 < discount < 100:
            price = price * (100 - discount) / 100

        lesson = await db.fetchrow(
            '''
            UPDATE public.lessons
            SET 
                title = $2,
                description = $3, 
                category_id = $4,
                logo = $5, 
                link = $6, 
                price = $7, 
                discount = $8, 
                tag_ids = $9, 
                testing_count = $10, 
                testing_state = $11
            WHERE id = $1
            RETURNING *
            ''',
            lesson_id,
            title,
            description,
            category_id,
            logo,
            link,
            price,
            discount,
            tag_ids,
            testing_count,
            testing_state,
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
