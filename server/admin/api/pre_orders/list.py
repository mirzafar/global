from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class PreOrdersView(BaseAPIView):
    template_name = 'adminn/pre_orders.html'

    async def get(self, request, user):
        context = dict()
        status = IntUtils.to_int(request.args.get('status')) or 0

        data = await mongo.pre_orders.find({'status': status}).to_list(length=None)
        for x in data:
            if x.get('good_id') and ObjectId.is_valid(x['good_id']):
                x['good'] = await mongo.goods.find_one({'_id': ObjectId(x['good_id'])})

            if x.get('color_id') and ObjectId.is_valid(x['color_id']):
                x['color'] = await mongo.colors.find_one({'_id': ObjectId(x['color_id'])})

            if x.get('size_id') and ObjectId.is_valid(x['size_id']):
                x['size'] = await mongo.sizes.find_one({'_id': ObjectId(x['size_id'])})

        context['data'] = data
        context['status'] = status

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user):
        last_name = StrUtils.to_str(request.json.get('last_name'))
        first_name = StrUtils.to_str(request.json.get('first_name'))
        title = StrUtils.to_str(request.json.get('title'))
        good_id = StrUtils.to_str(request.json.get('good_id'))
        size_id = StrUtils.to_str(request.json.get('size_id'))
        color_id = StrUtils.to_str(request.json.get('color_id'))
        description = StrUtils.to_str(request.json.get('description'))
        phone_number = StrUtils.to_str(request.json.get('phone_number'))

        if not last_name:
            return response.json({
                '_success': False,
                'message': 'Required param(s): last_name'
            })

        if not phone_number:
            return response.json({
                '_success': False,
                'message': 'Required param(s): phone_number'
            })

        if (phone_number.startswith('87') and len(phone_number) == 11) or (
            phone_number.startswith('+7') and len(phone_number) == 12):
            pass
        else:
            return response.json({
                '_success': False,
                'message': 'Invalid phone number'
            })

        await mongo.pre_orders.insert_one({
            'last_name': last_name,
            'first_name': first_name,
            'title': title,
            'good_id': good_id,
            'size_id': size_id,
            'color_id': color_id,
            'description': description,
            'phone_number': phone_number,
            'created_at': datetime.now(),
            'status': 0,
        })

        return response.json({
            '_success': True
        })
