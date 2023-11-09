from core.db import mongo
from core.handlers import BaseAPIView


class RentCreateView(BaseAPIView):
    template_name = 'adminn/rents-create.html'

    async def get(self, request, user):
        context = dict()
        context['tools'] = await mongo.tools.find({'status': 0}).to_list(length=None)
        return self.render_template(request=request, **context)
