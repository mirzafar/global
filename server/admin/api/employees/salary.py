import datetime
import math
from calendar import monthrange

from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView
from utils.strs import StrUtils


class SalaryView(BaseAPIView):
    template_name = 'adminn/users-salary.html'

    async def get(self, request, user):
        context = dict()

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        # current_user
        current_user = await mongo.users.find_one({'_id': ObjectId(user.id)})
        context['current_user'] = current_user
        # end current_user

        start_date = request.args.get('start_date')
        stop_date = request.args.get('stop_date')
        user_id = StrUtils.to_str(request.args.get('user_id'))

        if start_date and stop_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            stop_date = datetime.datetime.strptime(stop_date, '%Y-%m-%d')
            stop_date.replace(hour=23, minute=59, second=59, microsecond=59)
        else:
            dtn = datetime.datetime.now()
            start_date = dtn.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            a = monthrange(dtn.year, dtn.month)
            stop_date = dtn.replace(day=a[1], hour=23, minute=59, second=59, microsecond=59)

        filter_obj = {
            'status': 0,
            'start_date': {'$gte': start_date, '$lte': stop_date}
        }

        filter_users = {'status': 0}

        if 'admin' not in current_user.get('scope', []):
            filter_obj['user_id'] = str(current_user['_id'])
            filter_users['_id'] = current_user['_id']

        if user_id:
            filter_obj['user_id'] = user_id
            filter_users['_id'] = ObjectId(user_id)

        context['user_id'] = user_id
        context['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
        context['stop_date'] = datetime.datetime.strftime(stop_date, '%Y-%m-%d')

        users_dict = {}
        users = await mongo.users.find(filter_users).to_list(length=None)
        context['users'] = users

        for user in users:
            tariff = None
            role = None
            if user.get('role_id') and ObjectId.is_valid(user['role_id']):
                tariff = await mongo.tariffs.find_one({'role_id': str(user['role_id']), 'status': 0})
                if tariff and tariff.get('tariff'):
                    tariff = tariff['tariff']
                role = await mongo.roles.find_one({'_id': ObjectId(user['role_id'])})
            users_dict[str(user['_id'])] = {
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'username': user.get('username'),
                'days': 0,
                'salary': 0,
                'role': role,
                'tariff': tariff
            }

        diary = await mongo.diary.aggregate([
            {'$match': filter_obj},
            {'$group': {'_id': '$user_id', 'days': {'$sum': 1}}}
        ]).to_list(length=None)
        for d in diary:
            _id = str(d['_id'])
            if users_dict.get(_id):
                item = users_dict[_id]
                if item.get('tariff'):
                    item['salary'] = math.ceil(d['days'] * item['tariff'] * 100) / 100
                item['days'] = d.get('days')

        context['data'] = [v for k, v in users_dict.items()]

        return self.render_template(request=request, **context)
