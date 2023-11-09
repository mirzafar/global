from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import TemplateHTTPView, BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class PreOrdersItemView(BaseAPIView):

    async def post(self, request, user, item_id):
        item_id = StrUtils.to_str(item_id)
        if not item_id or not ObjectId.is_valid(item_id):
            return response.json({
                '_success': False,
                'message': 'Item id not found'
            })

        action = StrUtils.to_str(request.json.get('action'))
        status = IntUtils.to_int(request.json.get('status')) or 0

        if action == 'change_status':
            await mongo.pre_orders.update_one({
                '_id': ObjectId(item_id)
            }, {
                '$set': {
                    'status': status
                }
            })

        return response.json({
            '_success': True
        })
