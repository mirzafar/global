from datetime import datetime

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import APIView


class CheckoutView(APIView):
    template_name = 'shop/checkout.html'

    async def get(self, request, user):
        context = dict()
        filter_obj = {
            'status': 0
        }

        session_key = request.ctx.session.get('session_key')
        cart = await mongo.carts.find_one({'status': 0, 'session_key': session_key})
        context['cart'] = cart
        context['cart_items'] = []
        if cart:
            cart_items = await mongo.cart_items.find({'status': 0, 'cart_id': str(cart.get('_id'))}).to_list(
                length=None)
            if cart_items:
                for item in cart_items:
                    if item.get('good_id'):
                        item['good'] = await mongo.goods.find_one({'_id': ObjectId(item['good_id'])})
                    context['cart_items'].append(item)

        info = await mongo.info.find_one({})
        context['info'] = info if info else {}
        return self.render_template(request=request, **context)

    async def post(self, request, user):
        action = request.json.get('action')
        cart_id = request.json.get('cart_id')

        fields = ['first_name', 'last_name', 'country', 'address', 'apartment', 'phone_number', 'email']

        dtn = datetime.now()

        for x in fields:
            if not request.json.get(x):
                return response.json({
                    '_success': False,
                    'message': f'Required param(s): {x}'
                })
        if not cart_id:
            return response.json({
                '_success': False,
                'message': 'Cart not found, try again'
            })

        cart_items = await mongo.cart_items.find({'cart_id': cart_id}).to_list(length=None)
        good_result = {}
        for x in cart_items:
            if ObjectId.is_valid(x.get('good_id')):
                filter_good = dict(
                    status=0,
                    _id=ObjectId(x['good_id'])
                )
                if x.get('color_id'):
                    filter_good['color_ids'] = {'$in': [x['color_id']]}
                if x.get('size_id'):
                    filter_good['size_ids'] = {'$in': [x['size_id']]}

                good = await mongo.goods.find_one(filter_good)

                if not good:
                    return response.json({
                        '_success': False,
                        'message': 'This product has been removed from sale.'
                    })

                if good.get('count') < x.get('amount'):
                    if good.get('count') == 0:
                        return response.json({
                            '_success': False,
                            'message': f'The product is not on sale'
                        })
                    else:
                        return response.json({
                            '_success': False,
                            'message': f'Only {good.get("count")} left for sale'
                        })

                good_result[str(good['_id'])] = {
                    '_id': good['_id'],
                    'count': good.get('count', 0) - x.get('amount')
                }

                await mongo.cart_items.update_one({'_id': x['_id']},
                                                  {'$set': {'purchase_price': x['amount'] * good['purchase_price']}})

            else:
                return response.json({
                    '_success': False,
                    'message': f'Product not found'
                })

        item = {k: v for k, v in request.json.items() if k in fields}
        item['status'] = 1
        item['created_at'] = dtn
        item['user_id'] = user.id

        if action == 'create':
            await mongo.carts.update_one({'_id': ObjectId(cart_id)}, {'$set': item})
            await mongo.cart_items.update_many({'cart_id': cart_id},
                                               {'$set': {'status': 1, 'created_at': dtn}})
            for k, v in good_result.items():
                await mongo.goods.update_one({'_id': v.get('_id')}, {'$set': {'count': v.get('count')}})

        return response.json({'_success': True})
