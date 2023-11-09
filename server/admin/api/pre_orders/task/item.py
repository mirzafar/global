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


class PreOrdersTasksItemView(BaseAPIView):
    template_name = 'adminn/pre_orders_task_item.html'

    async def get(self, request, user, item_id):
        context = dict()

        filter_obj = {
            '_id': ObjectId(item_id)
        }
        context['employees'] = await mongo.employees.find({'status': 0}).to_list(length=None)
        data = await mongo.pre_order_tasks.find_one(filter_obj)

        pre_orders = await mongo.pre_orders.find({'status': 0}).to_list(length=None)
        for x in pre_orders:
            if x.get('good_id') and ObjectId.is_valid(x['good_id']):
                x['good'] = await mongo.goods.find_one({'_id': ObjectId(x['good_id'])})

            if x.get('color_id') and ObjectId.is_valid(x['color_id']):
                x['color'] = await mongo.colors.find_one({'_id': ObjectId(x['color_id'])})

            if x.get('size_id') and ObjectId.is_valid(x['size_id']):
                x['size'] = await mongo.sizes.find_one({'_id': ObjectId(x['size_id'])})
        context['pre_orders'] = pre_orders

        context['priority'] = PRIORITY
        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user, item_id):
        action = request.json.get("action")

        if action == 'edit':
            title = StrUtils.to_str(request.json.get('title'))
            pre_order_id = StrUtils.to_str(request.json.get('pre_order_id'))
            employee_ids = ListUtils.to_list_of_strs(request.json.get('employee_ids'))
            description = StrUtils.to_str(request.json.get('description'))
            deadline = StrUtils.to_str(request.json.get('deadline'))
            priority = IntUtils.to_int(request.json.get('priority'))
            status = IntUtils.to_int(request.json.get('status')) or 0
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

            await mongo.pre_order_tasks.update_one({'_id': ObjectId(item_id)}, {
                '$set': {
                    'title': title,
                    'pre_order_id': pre_order_id,
                    'employee_ids': employee_ids,
                    'description': description,
                    'priority': priority,
                    'deadline': deadline,
                    'photo': photo,
                    'created_at': datetime.now(),
                    'status': status,
                }})

        elif action == 'delete':
            await mongo.pre_order_tasks.update_one({'_id': ObjectId(item_id)}, {'$set': {'status': -1}})

        return response.json({
            '_success': True
        })
