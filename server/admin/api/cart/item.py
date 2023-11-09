import math
import uuid

from bson import ObjectId
from sanic import response

from core.db import mongo
from sanic.views import HTTPMethodView
from utils.ints import IntUtils
from utils.strs import StrUtils


class CartItemView(HTTPMethodView):

    @classmethod
    async def refresh_cart(cls, cart_id):
        if cart_id:
            cart = await mongo.carts.find_one({'_id': ObjectId(cart_id)})
            if cart:
                result = await mongo.cart_items.aggregate([
                    {'$match': {'status': 0, 'cart_id': cart_id}},
                    {'$group': {'_id': None, 'summa': {'$sum': '$summa'}}}
                ]).to_list(length=None)
                if result:
                    summa = math.ceil(result[0].get('summa', 0) * 100) / 100
                else:
                    summa = 0

                await mongo.carts.update_one({'_id': ObjectId(cart_id)},
                                             {'$set': {'summa': summa}})
                return summa
            else:
                return None
        else:
            return None

    async def post(self, request):
        action = StrUtils.to_str(request.json.get('action'))
        good_id = StrUtils.to_str(request.json.get('good_id'))
        amount = IntUtils.to_int(request.json.get('amount')) or 1
        size_id = StrUtils.to_str(request.json.get('size_id'))
        color_id = StrUtils.to_str(request.json.get('color_id'))
        cart_item_id = StrUtils.to_str(request.json.get('cart_item_id'))
        session_key = StrUtils.to_str(request.ctx.session.get('session_key'))

        if not session_key:
            session_key = str(uuid.uuid1())
            request.ctx.session['session_key'] = session_key

        good = await mongo.goods.find_one({'_id': ObjectId(good_id)})
        if not cart_item_id or not ObjectId.is_valid(cart_item_id):
            if action in ['remove_in_order', 'edit_in_order']:
                return response.json({
                    '_success': False,
                    'message': ''
                })

        if not good:
            return response.json({
                '_success': False,
                'message': 'Товар не найден'
            })

        if action == 'add_to_cart':
            cart = await mongo.carts.find_one({'status': 0, 'session_key': session_key})
            if not cart:
                insertedId = await mongo.carts.insert_one({
                    'status': 0,
                    'session_key': session_key,
                    'summa': 0.0
                })

                cart = {'_id': insertedId.inserted_id}

            cart_item = await mongo.cart_items.find_one(
                {'status': 0, 'good_id': good_id, 'cart_id': str(cart.get('_id')), 'color_id': color_id,
                 'size_id': size_id})

            if cart_item:
                await mongo.cart_items.update_one({'_id': cart_item['_id']}, {'$set': {
                    'amount': amount,
                    'summa': float(good.get('price', 0.0)) * amount
                }})

            else:
                await mongo.cart_items.insert_one({
                    'status': 0,
                    'good_id': good_id,
                    'size_id': size_id,
                    'color_id': color_id,
                    'amount': amount,
                    'summa': float(good.get('price', 0.0)) * amount,
                    'cart_id': str(cart.get('_id'))
                })

            await self.refresh_cart(cart_id=str(cart['_id']))

        elif action == 'remove_in_order':
            cart_item = await mongo.cart_items.find_one({'_id': ObjectId(cart_item_id)})
            if cart_item:
                await mongo.cart_items.update_one(
                    {'_id': ObjectId(cart_item_id)}, {'$set': {'status': -1}})

                await self.refresh_cart(cart_id=str(cart_item['cart_id']))

        elif action == 'edit_in_order':
            cart_item = await mongo.cart_items.find_one({'_id': ObjectId(cart_item_id)})
            if cart_item:
                await mongo.cart_items.update_one(
                    {'_id': ObjectId(cart_item_id)},
                    {'$set': {'amount': amount, 'summa': float(good.get('price', 0.0)) * amount}})
                await self.refresh_cart(cart_id=cart_item.get('cart_id'))

        return response.json({
            '_success': True
        })
