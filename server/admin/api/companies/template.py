from core.handlers import BaseAPIView


class CompaniesTemplateView(BaseAPIView):
    template_name = 'admin/companies.html'

    async def get(self, request, user):
        return self.render_template(request, user)
