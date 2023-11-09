import math
from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.floats import FloatUtils
from utils.strs import StrUtils


class RentItemView(BaseAPIView):
    template_name = 'adminn/rents-item.html'

    async def get(self, request, user, rent_id):
        rent_id = StrUtils.to_str(rent_id)
        if not rent_id or not ObjectId.is_valid(rent_id):
            return response.json({
                '_success': False,
                'message': 'Required param rent id'
            })

        item = await mongo.rents.find_one({'_id': ObjectId(rent_id)})

        context = dict()
        context['item'] = item
        context['tools'] = await mongo.tools.find({'status': 0}).to_list(length=None)

        return self.render_template(request=request, **context)

    async def post(self, request, user, rent_id):
        rent_id = StrUtils.to_str(rent_id)
        if not rent_id or not ObjectId.is_valid(rent_id):
            return response.json({
                '_success': False,
                'message': 'Required param rent id'
            })
        rent = await mongo.rents.find_one({'_id': ObjectId(rent_id)})

        action = StrUtils.to_str(request.json.get('action'))
        tool_id = StrUtils.to_str(request.json.get('tool_id'))

        set_update = dict()

        if action == 'update':
            last_name = StrUtils.to_str(request.json.get('last_name'))
            first_name = StrUtils.to_str(request.json.get('first_name'))
            middle_name = StrUtils.to_str(request.json.get('middle_name'))
            iin = StrUtils.to_str(request.json.get('iin'))
            description = StrUtils.to_str(request.json.get('description'))
            phone_number = StrUtils.to_str(request.json.get('phone_number'))
            address = StrUtils.to_str(request.json.get('address'))
            photo = StrUtils.to_str(request.json.get('photo'))

            if any([
                not last_name,
                not first_name
            ]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): first_name, last_name'
                })

            if iin and len(iin) == 11:
                pass
            else:
                return response.json({
                    '_success': False,
                    'message': 'Invalid iin'
                })

            if tool_id and ObjectId.is_valid(tool_id):
                if not rent.get('tool_id') == tool_id:
                    await mongo.tools.update_one({'_id': ObjectId(rent['tool_id'])}, {'$set': {'status': 0}})
            else:
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): tool id'
                })

            if phone_number:
                if (phone_number.startswith('+7') and len(phone_number) == 12) or (
                        phone_number.startswith('87') and len(phone_number) == 11):
                    pass
                else:
                    return response.json({
                        '_success': False,
                        'message': 'Invalid phone number'
                    })
            else:
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): phone number'
                })

            if any([
                not address,
                not photo
            ]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): address or photo'
                })

            await mongo.tools.update_one({'_id': ObjectId(tool_id)}, {'$set': {'status': 1}})
            set_update = {
                'last_name': last_name,
                'first_name': first_name,
                'middle_name': middle_name,
                'iin': iin,
                'tool_id': tool_id,
                'phone_number': phone_number,
                'address': address,
                'description': description,
                'photo': photo,
                'status': 0
            }

        elif action == 'stop':
            await mongo.tools.update_one({'_id': ObjectId(rent['tool_id'])}, {'$set': {'status': 0}})

            stop_date = datetime.now()
            diff = stop_date - rent['start_date']

            price = await mongo.tools.find_one({'_id': ObjectId(rent['tool_id'])})
            price = FloatUtils.to_float(price['price']) or 0
            set_update = {
                'stop_date': stop_date,
                'summa': math.ceil((diff.total_seconds() / 3600) * price * 100) / 100,
                'status': 1
            }

        elif action == 'delete':
            await mongo.tools.update_one({'_id': ObjectId(rent['tool_id'])}, {'$set': {'status': 0}})

            set_update = {
                'stop_date': datetime.now(),
                'status': -1
            }

        set_update['updated_at'] = datetime.now()

        await mongo.rents.update_one({'_id': ObjectId(rent_id)}, {'$set': set_update})

        return response.json({
            '_success': True
        })
