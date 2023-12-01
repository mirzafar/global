from core.handlers import BaseAPIView


class VisitsTemplateView(BaseAPIView):
    template_name = 'admin/visits.html'

    async def get(self, request, user):
        return self.render_template(request, user)


class VisitsTemplateItemView(BaseAPIView):
    template_name = 'admin/visits-item.html'

    async def get(self, request, user, visit_id):
        self.context = {
            'visit_id': visit_id
        }

        return self.render_template(request, user)
