from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.strs import StrUtils


class ReceiptsView(BaseAPIView):
    template_name = 'adminn/receipts.html'

    async def get(self, request, user):
        context = dict()

        data = []
        async for rc in mongo.receipts.find({'status': 0}).sort('_id', -1):
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
        action = StrUtils.to_str(request.json.get('action', ''))
        title = StrUtils.to_str(request.json.get('title', ''))
        description = StrUtils.to_str(request.json.get('description', ''))
        good_id = StrUtils.to_str(request.json.get('good_id', ''))
        email = StrUtils.to_str(request.json.get('email', ''))
        wpp = StrUtils.to_str(request.json.get('wpp', ''))
        tg = StrUtils.to_str(request.json.get('tg', ''))
        phone_number = StrUtils.to_str(request.json.get('phone_number', ''))
        receipt_id = StrUtils.to_str(request.json.get('receipt_id'))

        if action == 'create':
            if not all([title, description, phone_number, email]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s)'
                })

            await mongo.receipts.insert_one({
                'title': title,
                'description': description,
                'good_id': good_id,
                'email': email,
                'wpp': wpp,
                'tg': tg,
                'phone_number': phone_number,
                'state': 0,
                'status': 0
            })

            return response.json({
                '_success': True
            })

        elif action == 'delete':
            if not receipt_id:
                return response.json({
                    '_success': False,
                    'message': 'Required param: id'
                })

            await mongo.receipts.update_one({'_id': ObjectId(receipt_id)}, {'$set': {'status': -1}})

            return response.json({
                '_success': True
            })

        elif action == 'complete':
            if not receipt_id:
                return response.json({
                    '_success': False,
                    'message': 'Required param: id'
                })

            await mongo.receipts.update_one({'_id': ObjectId(receipt_id)}, {'$set': {'state': 1}})

            return response.json({
                '_success': True
            })

        return response.json({
            '_success': True
        })
