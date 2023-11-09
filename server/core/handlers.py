from jinja2 import Environment, select_autoescape, FileSystemLoader
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import html
from sanic.views import HTTPMethodView

from core.auth import auth
from settings import settings

root_dir = settings.get('root_dir')
TEMPLATE_DIR = '/'.join(root_dir.split('/')[:-1])

env = Environment(
    loader=FileSystemLoader(f'{TEMPLATE_DIR}/templates'),
    autoescape=select_autoescape()
)


class TemplateHTTPView(HTTPMethodView):
    template_name = None
    user = None

    def render_template(self, request: Request, **kwargs) -> html:
        template = env.get_template(self.template_name)
        rendered = template.render(
            request=request,
            app=request.app,
            url_for=request.app.url_for,
            _user=self.user,
            **kwargs
        )
        return HTTPResponse(rendered, content_type='text/html')


class BaseAPIView(TemplateHTTPView):
    decorators = [auth.login_required()]
