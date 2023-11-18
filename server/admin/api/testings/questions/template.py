from core.handlers import BaseAPIView


class TestingsQuestionsTemplatesView(BaseAPIView):
    template_name = 'admin/testings.html'

    async def get(self, request, user, lesson_id):
        return self.render_template(request, user)
