from core.handlers import BaseAPIView


class MainView(BaseAPIView):
    template_name = 'admin/main.html'

    async def get(self, request, user):
        # CURRENT USER
        self.user = user

        return self.render_template(
            request=request
        )
