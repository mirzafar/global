import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.strs import StrUtils


class OrdersView(BaseAPIView):
    template_name = 'adminn/orders.html'

    async def get(self, request, user):
        context = dict()

        data = []
        async for rc in mongo.receipts.find({}).sort('_id', -1):
            if rc.get('good_id') and ObjectId.is_valid(rc['good_id']):
                rc['good_id'] = await mongo.goods.find_one({'_id': ObjectId(rc['good_id'])})
            else:
                rc['good_id'] = {}
            data.append(rc)

        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user):
        action = StrUtils.to_str(request.json.get('action'))
        title = StrUtils.to_str(request.json.get('title'))
        description = StrUtils.to_str(request.json.get('description'))
        receipt_id = StrUtils.to_str(request.json.get('receipt_id'))
        employee_id = StrUtils.to_str(request.json.get('employee_id'))
        start_date = StrUtils.to_str(request.json.get('start_date'))
        stop_date = StrUtils.to_str(request.json.get('stop_date'))

        if action == 'create':
            if not all([title, description, employee_id, start_date, stop_date]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s)'
                })

            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            stop_date = datetime.datetime.strptime(stop_date, '%Y-%m-%d')

            await mongo.orders.insert_one({
                'title': title,
                'description': description,
                'receipt_id': receipt_id,
                'employee_id': employee_id,
                'start_date': start_date,
                'stop_date': stop_date,
                'status': 0
            })

            return response.json({
                '_success': True
            })

        return response.json({
            '_success': True
        })
