from bson import ObjectId

from core.db import mongo
from core.handlers import APIView


class CartView(APIView):
    template_name = 'shop/cart.html'

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
