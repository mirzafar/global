from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils


class CustomersTemplateView(BaseAPIView):
    template_name = 'admin/customers.html'

    async def get(self, request, user):
        return self.render_template(request=request, user=user)


class CustomersItemTemplateView(BaseAPIView):
    template_name = 'admin/customers-item.html'

    async def get(self, request, user, customer_id):
        customer_id = IntUtils.to_int(customer_id)
        customer = dict(await db.fetchrow(
            '''
            SELECT *
            FROM public.customers
            WHERE id = $1
            ''',
            customer_id
        ) or {})

        self.context = {
            'data': customer,
        }

        return self.render_template(request=request, user=user)


class CustomersCreateTemplateView(BaseAPIView):
    template_name = 'admin/customers-create.html'

    async def get(self, request, user, customer_id):
        return self.render_template(request=request, user=user)
