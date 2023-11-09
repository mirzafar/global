from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class ExpensesView(BaseAPIView):
    template_name = 'adminn/analytics/expenses.html'

    async def get(self, request, user):
        context = dict()

        filter_obj = {
            'status': 0,
        }
        data = []
        async for expense in mongo.expenses.find(filter_obj).sort('_id', -1):
            data.append(expense)

        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
