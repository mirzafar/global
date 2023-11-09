import math

from bson import ObjectId
from sanic import response

from core.db import mongo
from utils.floats import FloatUtils
from core.handlers import BaseAPIView, TemplateHTTPView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class GoodItemView(BaseAPIView):
    template_name = 'adminn/good-item.html'

    async def get(self, request, user, good_id):
        context = dict()
        filter_obj = {
            '_id': ObjectId(good_id)
        }
        context['category'] = await mongo.category.find({'status': 0}).to_list(length=None)
        context['colors'] = await mongo.colors.find({'status': 0}).to_list(length=None)
        context['sizes'] = await mongo.sizes.find({'status': 0}).to_list(length=None)
        context['brands'] = await mongo.brands.find({'status': 0}).to_list(length=None)
        context['overheads'] = await mongo.overheads.find({'status': 0}).to_list(length=None)
        data = await mongo.goods.find_one(filter_obj)

        if data.get('price') and data.get('discount'):
            data['price'] = math.ceil(float(data['price']) * 100 / (100 - float(data['discount'])) * 100) / 100

        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)

    async def post(self, request, user, good_id):
        action = request.json.get("action")
        if action == 'edit':
            print('edit product -->', request.json)
            title = StrUtils.to_str(request.json.get('title'))
            description = StrUtils.to_str(request.json.get('description'))
            category_id = StrUtils.to_str(request.json.get('category_id'))
            color_ids = ListUtils.to_list_of_strs(request.json.get('color_ids')) or []
            size_ids = ListUtils.to_list_of_strs(request.json.get('size_ids')) or []
            brand_id = StrUtils.to_str(request.json.get('brand_id'))
            overhead_id = StrUtils.to_str(request.json.get('overhead_id'))
            price = FloatUtils.to_float(request.json.get('price')) or 0.0
            purchase_price = FloatUtils.to_float(request.json.get('purchase_price')) or 0.0
            old_price = FloatUtils.to_float(request.json.get('old_price')) or 0.0
            discount = FloatUtils.to_float(request.json.get('discount')) or 0.0
            count = IntUtils.to_int(request.json.get('count')) or 0
            photo = StrUtils.to_str(request.json.get('photo'))
            is_new = request.json.get('is_new')
            is_hot = request.json.get('is_hot')

            if not all([
                title, price, category_id, purchase_price, overhead_id
            ]):
                return response.json({
                    '_success': False,
                    'message': 'Required param(s): title, price, category id, purchase price, overhead_id'
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

            mongo.goods.update_one({'_id': ObjectId(good_id)}, {'$set': {
                'title': title,
                'description': description,
                'category_id': category_id,
                'color_ids': color_ids,
                'overhead_id': overhead_id,
                'size_ids': size_ids,
                'brand_id': brand_id,
                'price': price,
                'purchase_price': purchase_price,
                'old_price': old_price,
                'discount': discount,
                'photo': photo,
                'status': 0,
                'count': count,
                'all_count': count,
                'is_new': is_new,
                'is_hot': is_hot,
            }})

        elif action == 'delete':
            await mongo.goods.update_one({'_id': ObjectId(good_id)}, {'$set': {'status': -1}})

        return response.json({
            '_success': True
        })
