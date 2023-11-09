import math
from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils

PRIORITY = {
    0: "Обычный",
    1: "Низкий",
    2: "Средний",
    3: "Высокий",
    4: "Критичный",
    5: "Неотложный",
    6: "Срочный"
}


class PreOrdersTasksView(BaseAPIView):
    template_name = 'adminn/pre_orders_task_list.html'

    async def get(self, request, user):
        limit = IntUtils.to_int(request.args.get('limit')) or 16
        page = IntUtils.to_int(request.args.get('page')) or 1
        status = IntUtils.to_int(request.args.get('status')) or 0
        employee_id = StrUtils.to_str(request.args.get('employee_id')) or user.id

        skip = (page - 1) * limit

        context = {'data': []}
        filter_obj = {
            'status': status
        }

        if employee_id:
            filter_obj['employee_ids'] = {
                '$in': [employee_id]
            }

        data = await mongo.pre_order_tasks.find(filter_obj).sort('_id', -1).skip(skip).limit(limit).to_list(length=None)

        total = await mongo.pre_order_tasks.count_documents(filter_obj)
        context['page'] = page
        context['_range'] = math.ceil(total / limit)

        for x in data:
            if x.get('user_id') and ObjectId.is_valid(x['user_id']):
                x['user'] = await mongo.users.find_one({'_id': ObjectId(x['user_id'])})

            context['data'].append(x)

        context['employees'] = await mongo.employees.find({'status': 0}).to_list(length=None)

        context['status'] = status
        context['employee_id'] = employee_id

        context['priority'] = PRIORITY

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request):
        title = StrUtils.to_str(request.json.get('title'))
        pre_order_id = StrUtils.to_str(request.json.get('pre_order_id'))
        employee_ids = ListUtils.to_list_of_strs(request.json.get('employee_ids'))
        description = StrUtils.to_str(request.json.get('description'))
        deadline = StrUtils.to_str(request.json.get('deadline'))
        priority = IntUtils.to_int(request.json.get('priority'))
        photo = StrUtils.to_str(request.json.get('photo'))

        if any([
            not title,
            not employee_ids,
            not description
        ]):
            return response.json({
                '_success': False,
                'message': 'Required param(s): title, employee, description'
            })

        await mongo.pre_order_tasks.insert_one({
            'user_id': "64363b1b016f226444e54a91",  # user.id,
            'title': title,
            'pre_order_id': pre_order_id,
            'employee_ids': employee_ids,
            'description': description,
            'priority': priority,
            'deadline': deadline,
            'photo': photo,
            'created_at': datetime.now(),
            'status': 0,
        })

        return response.json({
            '_success': True
        })
