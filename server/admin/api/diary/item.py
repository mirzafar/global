import datetime

from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class DiaryItemView(BaseAPIView):
    template_name = 'adminn/diary-item.html'

    async def get(self, request, user, diary_id):

        filter_obj = {
            '_id': ObjectId(diary_id)
        }

        users = await mongo.users.find({'status': 0}).to_list(length=None)
        data = await mongo.diary.find_one(filter_obj)

        if data and data.get('start_date'):
            data['start_date'] = datetime.datetime.strftime(data['start_date'], '%H:%M')

        if data and data.get('stop_date'):
            data['stop_date'] = datetime.datetime.strftime(data['stop_date'], '%H:%M')

        # CURRENT USER
        user = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(
            request=request,
            data=data,
            users=users,
            user=user
        )
