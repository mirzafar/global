import datetime
import math

from bson import ObjectId
from sanic import response

from core.db import mongo
from utils.floats import FloatUtils
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class GoodsView(BaseAPIView):
    template_name = 'adminn/goods.html'

    async def get(self, request, user):
        limit = IntUtils.to_int(request.args.get('limit')) or 4
        page = IntUtils.to_int(request.args.get('page')) or 1
        skip = (page - 1) * limit

        context = {'data': []}
        filter_obj = {
            'status': 0
        }

        goods = await mongo.goods.find(filter_obj).sort('_id', -1).skip(skip).limit(limit).to_list(length=None)

        total = await mongo.goods.count_documents(filter_obj)
        context['_range'] = math.ceil(total / limit)
        context['page'] = page

        for good in goods:
            if good.get('category_id') and ObjectId.is_valid(good['category_id']):
                good['category'] = await mongo.category.find_one({'_id': ObjectId(good['category_id'])})
            context['data'].append(good)

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user):
        action = request.json.get("action")
        if action == 'create':
            title = StrUtils.to_str(request.json.get('title'))
            description = StrUtils.to_str(request.json.get('description')) or ''
            category_id = StrUtils.to_str(request.json.get('category_id'))
            color_ids = ListUtils.to_list_of_strs(request.json.get('color_ids')) or []
            size_ids = ListUtils.to_list_of_strs(request.json.get('size_ids')) or []
            brand_id = StrUtils.to_str(request.json.get('brand_id'))
            overhead_id = StrUtils.to_str(request.json.get('overhead_id'))
            price = FloatUtils.to_float(request.json.get('price')) or 0.0
            old_price = FloatUtils.to_float(request.json.get('old_price')) or 0.0
            purchase_price = FloatUtils.to_float(request.json.get('purchase_price')) or 0.0
            discount = FloatUtils.to_float(request.json.get('discount')) or 0.0
            photo = StrUtils.to_str(request.json.get('photo'))
            count = IntUtils.to_int(request.json.get('count')) or 0
            is_new = request.json.get('is_new')
            is_hot = request.json.get('is_hot')

            if not all([
                title, price, category_id, purchase_price, overhead_id
            ]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): title, price, category id, purchase_price, overhead_id'
                })

            if any([
                price < 0,
                purchase_price < 0,
                old_price < 0,
                discount < 0,
                count < 0,
            ]):
                return response.json({
                    '_success': False,
                    'message': 'Price, old price, discount, count cannot be less than 0'
                })

            if discount and price:
                price = math.ceil(price * (100 - discount) / 100 * 100) / 100

            await mongo.goods.insert_one({
                'title': title,
                'description': description,
                'category_id': category_id,
                'color_ids': color_ids,
                'size_ids': size_ids,
                'brand_id': brand_id,
                'price': price,
                'purchase_price': purchase_price,
                'old_price': old_price,
                'overhead_id': overhead_id,
                'discount': discount,
                'photo': photo,
                'status': 0,
                'is_new': is_new,
                'is_hot': is_hot,
                'count': count,
                'all_count': count,
                'created_at': datetime.datetime.now()
            })

        elif action == 'delete':
            _id = request.json.get('_id')
            await mongo.goods.update_one({'_id': ObjectId(_id)}, {'$set': {'status': -1}})

        return response.json({
            '_success': True
        })
