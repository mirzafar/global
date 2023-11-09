from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class DiaryCreateView(BaseAPIView):
    template_name = 'adminn/diary-create.html'

    async def get(self, request, user):
        context = dict()
        context['users'] = await mongo.users.find({'status': 0}).to_list(length=None)

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
