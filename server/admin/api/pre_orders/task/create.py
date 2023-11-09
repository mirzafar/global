from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView

PRIORITY = {
    0: "Обычный",
    1: "Низкий",
    2: "Средний",
    3: "Высокий",
    4: "Критичный",
    5: "Неотложный",
    6: "Срочный"
}


class PreOrderTaskCreateView(BaseAPIView):
    template_name = 'adminn/pre_order_task_create.html'

    async def get(self, request, user):
        context = dict()

        pre_orders = await mongo.pre_orders.find({'status': 0}).to_list(length=None)
        for x in pre_orders:
            if x.get('good_id') and ObjectId.is_valid(x['good_id']):
                x['good'] = await mongo.goods.find_one({'_id': ObjectId(x['good_id'])})

            if x.get('color_id') and ObjectId.is_valid(x['color_id']):
                x['color'] = await mongo.colors.find_one({'_id': ObjectId(x['color_id'])})

            if x.get('size_id') and ObjectId.is_valid(x['size_id']):
                x['size'] = await mongo.sizes.find_one({'_id': ObjectId(x['size_id'])})

        context['pre_orders'] = pre_orders
        context['employees'] = await mongo.employees.find({'status': 0}).to_list(length=None)
        context['priority'] = PRIORITY

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
