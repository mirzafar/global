from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class ApplicationsView(BaseAPIView):
    template_name = 'adminn/applications.html'

    async def get(self, request, user):
        data = await mongo.applications.find({'status': 0}).sort('_id', -1).to_list(length=None)

        # CURRENT USER
        user = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(
            request=request,
            data=data,
            user=user
        )

    async def post(self, request, user):
        pass
