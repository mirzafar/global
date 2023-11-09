import math

from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import TemplateHTTPView
from utils.ints import IntUtils
from utils.strs import StrUtils


class StoryView(TemplateHTTPView):
    template_name = 'shop/shop.html'

    async def get(self, request):
        action = StrUtils.to_str(request.args.get('action'))
        good_id = StrUtils.to_str(request.args.get('good_id'))
        category_ids = [x for x in request.args.get('category_ids', '').split(',') if x]
        brand_ids = [x for x in request.args.get('brand_ids', '').split(',') if x]
        size_ids = [x for x in request.args.get('size_ids', '').split(',') if x]
        color_ids = [x for x in request.args.get('color_ids', '').split(',') if x]
        q = StrUtils.to_str(request.args.get('q'))

        sort = StrUtils.to_str(request.args.get('sort'))
        if sort and ':' in sort:
            sort_name, sort_number = sort.split(':')
            sort_number = IntUtils.to_int(sort_number)
        else:
            sort_name, sort_number = '_id', -1

        start_price = IntUtils.to_int(request.args.get('start_price'))
        end_price = IntUtils.to_int(request.args.get('end_price'))

        page = IntUtils.to_int(request.args.get('page', 1)) or 1
        limit = IntUtils.to_int(request.args.get('limit', 15)) or 15
        skip = (page - 1) * limit

        if action == 'get_good':
            item = await mongo.goods.find_one({'_id': ObjectId(good_id)},
                                              projection={'created_at': False})

            if item:
                item['_id'] = str(item['_id'])

            if item.get('color_ids'):
                item['colors'] = []
                color_ids = item.pop('color_ids', None)
                color_ids = [ObjectId(x) for x in color_ids if ObjectId.is_valid(x)]
                colors = await mongo.colors.find({'_id': {'$in': color_ids}}).to_list(length=None)
                if colors:
                    for color in colors:
                        item['colors'].append({
                            '_id': str(color['_id']),
                            'title': color.get('title')
                        })

            if item.get('category_id'):
                item['category'] = ''
                category_id = item.pop('category_id')
                if ObjectId.is_valid(category_id):
                    category = await mongo.category.find_one({'_id': ObjectId(category_id)})
                    item['category'] = category.get('title')

            if item.get('size_ids'):
                item['sizes'] = []
                size_ids = item.pop('size_ids', None)
                size_ids = [ObjectId(x) for x in size_ids if ObjectId.is_valid(x)]
                sizes = await mongo.sizes.find({'_id': {'$in': size_ids}}).to_list(length=None)
                if sizes:
                    for size in sizes:
                        item['sizes'].append({
                            '_id': str(size['_id']),
                            'title': size.get('title')
                        })

            if item.get('brand_id'):
                item['brand'] = ''
                brand_id = item.pop('brand_id')
                if ObjectId.is_valid(brand_id):
                    brand = await mongo.brands.find_one({'_id': ObjectId(brand_id)})
                    item['brand'] = brand.get('title')

            return response.json({
                '_success': True,
                'item': item
            })

        context = dict()
        filter_obj = {
            'status': 0
        }

        if q:
            filter_obj['title'] = {
                '$regex': q,
                "$options": "i"
            }

        if category_ids:
            filter_obj['category_id'] = {'$in': category_ids}
            context['category_ids'] = category_ids

        if brand_ids:
            filter_obj['brand_id'] = {'$in': brand_ids}
            context['brand_ids'] = brand_ids

        if size_ids:
            filter_obj['size_id'] = {'$in': size_ids}
            context['size_ids'] = size_ids

        if color_ids:
            filter_obj['color_id'] = {'$in': color_ids}
            context['color_ids'] = color_ids

        if start_price:
            filter_obj['price'] = {
                '$gte': start_price
            }

        if end_price:
            filter_obj['price'] = {
                '$lte': end_price
            }

        category = await mongo.category.find({'status': 0}).to_list(length=None)
        category_counts = await mongo.goods.aggregate([
            {'$match': {'status': 0}},
            {'$group': {'_id': '$category_id', 'count': {'$sum': 1}}}
        ]).to_list(length=None)

        data_category = dict()

        for ct in category:
            data_category[str(ct['_id'])] = {
                '_id': str(ct['_id']),
                'title': ct.get('title'),
                'count': 0
            }

        for cc in category_counts:
            if data_category.get(str(cc['_id'])):
                data_category[str(cc['_id'])]['count'] = cc.get('count', 0)

        context['category'] = [v for k, v in data_category.items()]
        context['sizes'] = await mongo.sizes.find({'status': 0}).to_list(length=None)
        context['colors'] = await mongo.colors.find({'status': 0}).to_list(length=None)
        context['brands'] = await mongo.brands.find({'status': 0}).to_list(length=None)

        goods = await mongo.goods.find(filter_obj, limit=limit, skip=skip).sort(sort_name, sort_number).to_list(
            length=None)

        data = list()

        for good in goods:
            if good.get('category_id') and ObjectId.is_valid(good['category_id']):
                good['category'] = await mongo.category.find_one({'_id': ObjectId(good['category_id'])})
            data.append(good)

        context['goods'] = data
        context['_total'] = await mongo.goods.count_documents(filter_obj)
        context['_count_page'] = math.ceil(context['_total'] / limit) if context['_total'] > 0 else 1
        context['_prev_page'] = True if page > 1 else False
        context['_next_page'] = True if context['_count_page'] < page else False
        context['_current_page'] = page

        context['q'] = q
        context['start_price'] = start_price
        context['end_price'] = end_price

        session_key = request.ctx.session.get('session_key')
        cart = await mongo.carts.find_one({'status': 0, 'session_key': session_key})
        context['cart'] = cart if cart else {}
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

        context['show_start'] = (page * limit) - limit + 1
        show_end = page * limit
        if show_end > context['_total']:
            show_end = context.get('_total')

        context['show_end'] = show_end
        context['sort'] = sort

        return self.render_template(request=request, **context)
