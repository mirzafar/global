import math

from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView
from utils.ints import IntUtils


class ApproveView(BaseAPIView):
    template_name = 'adminn/approve.html'

    async def get(self, request, user):
        limit = IntUtils.to_int(request.args.get('limit')) or 15
        page = IntUtils.to_int(request.args.get('page')) or 1
        skip = (page - 1) * limit

        context = dict()

        status = int(request.args.get('status', 1))
        filter_obj = {'status': status}

        context['data'] = await mongo.carts.find(filter_obj).sort('_id', -1).skip(skip).limit(limit).to_list(
            length=None)

        total = await mongo.carts.count_documents(filter_obj)
        context['page'] = page
        context['_range'] = math.ceil(total / limit)

        context['status'] = status

        info = await mongo.info.find_one({})
        context['info'] = info if info else {}

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
