from functools import partial, wraps
from inspect import isawaitable

from sanic import response

__all__ = ['auth']

from core.db import db


class Auth:
    app = None
    login_endpoint = None
    login_url = None
    session_name = None

    def initialize(self, app):
        if self.app is not None:
            raise RuntimeError('already initialized with an application')
        self.app = app
        self.login_endpoint = app.config.get('AUTH_LOGIN_ENDPOINT', None)
        self.login_url = app.config.get('AUTH_LOGIN_URL', None)
        self.session_name = app.config.get('AUTH_SESSION_NAME', app.config.get('SESSION_NAME', 'session'))

    @classmethod
    def get_auth_key(cls, user_id) -> str:
        return f'auth:user:{user_id}'

    def login_user(self, request, user):
        self.get_session(request)['user_id'] = user['id']

    def logout_user(self, request):
        return self.get_session(request).pop('user_id', None)

    async def current_user(self, request):
        user_id = self.get_session(request).get('user_id', None)
        if user_id is not None:
            user = await db.fetchrow(
                '''
                SELECT 
                    u.id, 
                    u.last_name,
                    u.first_name,
                    u.middle_name,
                    u.role_id,
                    u.status,
                    u.password,
                    u.username,
                    r.title AS role_title,
                    r.key AS role_key,
                    r.permissions AS permissions,
                    u.photo
                FROM public.users u
                LEFT JOIN public.roles r ON u.role_id = r.id
                WHERE u.id = $1
                ''',
                user_id
            )
            return user

    def login_required(
        self,
        route=None,
        *,
        user_keyword='user',
        handle_no_auth=None
    ):
        if route is None:
            return partial(
                self.login_required,
                user_keyword=user_keyword,
                handle_no_auth=handle_no_auth
            )

        if handle_no_auth is not None:
            assert callable(handle_no_auth), 'handle_no_auth must be callable'

        @wraps(route)
        async def privileged(request, *args, **kwargs):
            user = await self.current_user(request)
            if isawaitable(user):
                user = await user

            if user is None:
                if handle_no_auth:
                    resp = handle_no_auth(request)
                else:
                    resp = self.handle_no_auth(request)
            else:
                if user_keyword is not None:
                    if user_keyword in kwargs:
                        raise RuntimeError(
                            'override user keyword %r in route' % user_keyword
                        )

                    kwargs[user_keyword] = user

                resp = route(request, *args, **kwargs)

            if isawaitable(resp):
                resp = await resp
            return resp

        return privileged

    @classmethod
    def get_session(cls, request):
        return request.ctx.session

    def handle_no_auth(self, request):
        u = self.login_url or request.app.url_for(self.login_endpoint)
        return response.redirect(u)


auth = Auth()
