from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class ToolsView(BaseAPIView):
    template_name = 'adminn/tools.html'

    async def get(self, request, user):
        context = dict()

        context['states'] = {
            0: 'На складе',
            1: 'В аренде'
        }

        filter_obj = {
            'status': {
                '$ne': -1
            }
        }

        data = []
        async for tool in mongo.tools.find(filter_obj):
            data.append(tool)

        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
