from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class RentView(BaseAPIView):
    template_name = 'adminn/rents.html'

    async def get(self, request, user):
        status = IntUtils.to_int(request.args.get('status')) or 0
        context = dict()

        filter_obj = {
            'status': status
        }

        data = []
        async for x in mongo.rents.find(filter_obj):
            if x.get('tool_id'):
                x['tool'] = await mongo.tools.find_one({'_id': ObjectId(x['tool_id'])})

            data.append(x)

        context['data'] = data
        context['status'] = status
        return self.render_template(request=request, **context)

    async def post(self, request, user):
        last_name = StrUtils.to_str(request.json.get('last_name'))
        first_name = StrUtils.to_str(request.json.get('first_name'))
        middle_name = StrUtils.to_str(request.json.get('middle_name'))
        iin = StrUtils.to_str(request.json.get('iin'))
        tool_id = StrUtils.to_str(request.json.get('tool_id'))
        phone_number = StrUtils.to_str(request.json.get('phone_number'))
        address = StrUtils.to_str(request.json.get('address'))
        description = StrUtils.to_str(request.json.get('description'))
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
            tool = await mongo.tools.find_one({'status': 0})
            if not tool:
                return response.json({
                    '_success': False,
                    'message': 'This tool not found or in rent'
                })
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
        await mongo.rents.insert_one({
            'last_name': last_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'tool_id': tool_id,
            'description': description,
            'iin': iin,
            'phone_number': phone_number,
            'address': address,
            'photo': photo,
            'start_date': datetime.now(),
            'status': 0
        })

        return response.json({
            '_success': True
        })
