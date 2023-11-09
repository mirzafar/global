from bson import ObjectId
from sanic import response

from core.db import mongo
from core.handlers import BaseAPIView


class InfoView(BaseAPIView):
    template_name = 'adminn/info.html'

    async def get(self, request, user):
        data = await mongo.info.find_one({})
        user = await mongo.users.find_one({'_id': ObjectId(user.id)})
        return self.render_template(
            request=request,
            data=data if data else {},
            user=user
        )

    async def post(self, request, user):
        fields = ['name', 'phone_number', 'email', 'address', 'about_us', 'from_time', 'to_time', 'from_day', 'to_day',
                  'photo']
        item = {k: v for k, v in request.json.items() if k in fields}
        action = request.json.get('action')
        if action == 'edit':
            await mongo.info.find_one_and_update(
                {},
                {
                    '$set': item
                }, upsert=True)
        return response.json({
            '_success': True
        })
