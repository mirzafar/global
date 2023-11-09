import calendar
import math
from datetime import datetime

from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView
from utils.strs import StrUtils


class AnalyticsView(BaseAPIView):
    template_name = 'adminn/analytics/analytics.html'

    async def get(self, request, user):
        start_data = StrUtils.to_str(request.args.get('start_data'))
        stop_data = StrUtils.to_str(request.args.get('stop_data'))

        context = dict()
        dtn = datetime.now()

        if start_data:
            try:
                start_data = datetime.strptime(start_data, '%m/%d/%Y')
            except:
                start_data = datetime.strptime(start_data, '%Y-%m-%d')

            start_data.replace(hour=0, minute=0, second=0)
        else:
            start_data = dtn.replace(day=1, hour=0, minute=0, second=0)

        if stop_data:
            try:
                stop_data = datetime.strptime(stop_data, '%m/%d/%Y')
            except:
                stop_data = datetime.strptime(stop_data, '%Y-%m-%d')
            stop_data.replace(hour=23, minute=59, second=59)
        else:
            last_day = calendar.monthrange(dtn.year, dtn.month)
            stop_data = dtn.replace(day=last_day[1], hour=23, minute=59)

        context['start_data'] = str(start_data).split(' ')[0]
        context['stop_data'] = str(stop_data).split(' ')[0]

        filter_cart_items = {
            'status': 1,
            'created_at': {
                '$gte': start_data,
                '$lte': stop_data
            }
        }

        filter_rents = {
            'status': 1,
            'stop_date': {
                '$gte': start_data,
                '$lte': stop_data
            }
        }

        total = await mongo.cart_items.aggregate([
            {'$match': filter_cart_items},
            {'$group': {'_id': None, 'purchase_price': {'$sum': '$purchase_price'}, 'summa': {'$sum': '$summa'}}}
        ]).to_list(length=None)

        total = total[0] if total else {}
        purchase_price = total.get('purchase_price', 0)
        summa = total.get('summa', 0)

        context['good'] = {
            'purchase_price': math.ceil(purchase_price * 100) / 100,
            'summa': math.ceil(summa * 100) / 100,
            'arrived': math.ceil((summa - purchase_price) * 100) / 100,
        }

        filter_expenses = {
            'status': 0,
            'created_at': {
                '$gte': start_data,
                '$lte': stop_data
            }
        }

        total = await mongo.expenses.aggregate([
            {'$match': filter_expenses},
            {'$group': {'_id': None, 'summa': {'$sum': '$sum'}}}
        ]).to_list(length=None)

        total = total[0] if total else {}
        summa = total.get('summa', 0)

        context['expense'] = {
            'summa': summa,
        }

        total = await mongo.rents.aggregate([
            {'$match': filter_rents},
            {'$group': {'_id': None, 'summa': {'$sum': '$summa'}}}
        ]).to_list(length=None)

        context['rents'] = total[0] if total else {}

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
