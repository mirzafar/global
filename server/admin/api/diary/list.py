import datetime
import math

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class DiaryView(BaseAPIView):
    template_name = 'adminn/diary.html'

    async def get(self, request, user):
        dt = datetime.datetime.now()
        day = IntUtils.to_int(request.args.get('day', dt.day))
        month = IntUtils.to_int(request.args.get('month', dt.month))
        year = IntUtils.to_int(request.args.get('year', dt.year))

        limit = IntUtils.to_int(request.args.get('limit')) or 15
        page = IntUtils.to_int(request.args.get('page')) or 1
        skip = (page - 1) * limit

        employee_id = StrUtils.to_str(request.args.get('employee_id', user.id))

        context = dict()

        filter_obj = {
            'status': 0,
            'year': year,
            'month': month,
            'day': day,
            'user_id': str(employee_id),
        }

        data = await mongo.diary.find(filter_obj).sort('_id', -1).skip(skip).limit(limit).to_list(length=None)
        for x in data:
            if x.get('user_id') and ObjectId.is_valid(x['user_id']):
                x['user'] = await mongo.users.find_one({'_id': ObjectId(x['user_id'])})

        context['roles'] = await mongo.roles.find({'status': 0}).to_list(length=None)
        context['data'] = data

        context['users'] = await mongo.users.find({'status': 0}).to_list(length=None)

        context['page'] = page
        context['employee_id'] = employee_id

        total = await mongo.diary.count_documents(filter_obj)
        context['_range'] = math.ceil(total / limit)

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user):
        dt = datetime.datetime.now()
        diary_id = StrUtils.to_str(request.json.get('diary_id'))
        user_id = StrUtils.to_str(request.json.get('user_id'))
        description = StrUtils.to_str(request.json.get('description'))
        start_date = StrUtils.to_str(request.json.get('start_date'))
        stop_date = StrUtils.to_str(request.json.get('stop_date'))
        photo = request.json.get('photo')
        action = StrUtils.to_str(request.json.get('action'))

        if action == 'create':
            if not all([user_id, start_date]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s)'
                })
            try:
                hour, minute = start_date.split(':')
                start_date = dt.replace(hour=int(hour), minute=int(minute))
            except:
                return response.json({
                    '_success': False,
                    'message': 'Error start day and stop date'
                })

            duplicate = await mongo.diary.find_one({
                'day': dt.day,
                'user_id': user_id
            })

            if duplicate:
                return response.json({
                    '_success': False,
                    'message': 'You already have an open period'
                })

            await mongo.diary.insert_one({
                'user_id': user_id,
                'description': description,
                'start_date': start_date,
                'stop_date': None,
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
                'photo': photo,
                'status': 0
            })

            return response.json({
                '_success': True
            })

        elif action == 'edit':
            item = {}

            if not diary_id or not ObjectId.is_valid(diary_id):
                return response.json({
                    '_success': False,
                    'message': 'Required param: id'
                })

            if stop_date:
                try:
                    hour, minute = stop_date.split(':')
                    stop_date = dt.replace(hour=int(hour), minute=int(minute))
                except:
                    return response.json({
                        '_success': False,
                        'message': 'Error start day and stop date'
                    })

                item['stop_date'] = stop_date

            if description:
                item['description'] = description

            if user_id:
                item['user_id'] = user_id

            if photo:
                item['photo'] = photo

            await mongo.diary.update_one({'_id': ObjectId(diary_id)}, {'$set': item})

            return response.json({
                '_success': True
            })

        elif action == 'delete':
            if not diary_id:
                return response.json({
                    '_success': False,
                    'message': 'Required param: id'
                })

            await mongo.diary.update_one({'_id': ObjectId(diary_id)}, {'$set': {'status': -1}})

        return response.json({
            '_success': True
        })
