# import re
# from hashlib import md5
#
# from sanic import response
# from sanic.views import HTTPMethodView
#
# from adminn.authentication import UserSerializer
# from core.auth import auth
# from core.db import mongo
# from core.handlers import TemplateHTTPView, BaseAPIView
# from core.hasher import generate_password
# from utils.strs import StrUtils
#
# email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
# phone_regex = "^\\+?[1-9][0-9]{7,14}$"
# password_regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
#
#
# class LoginAPIView(TemplateHTTPView):
#     template_name = 'auth/api/login1.html'
#
#     async def get(self, request):
#         auth.logout_user(request)
#
#         return self.render_template(request=request)
#
#     async def post(self, request):
#         username = str(request.json.get('username', ''))
#         password = str(request.json.get('password', ''))
#
#         if not username and not password:
#             return response.json({
#                 '_success': False,
#                 'message': 'Required param(s)'
#             })
#
#         user = await mongo.clients.find_one({
#             'username': username,
#             'password': generate_password(password=password),
#             'status': {
#                 '$gte': 0
#             }
#         })
#
#         if not user:
#             return response.json({
#                 '_success': False,
#                 'message': 'user not found'
#             })
#
#         if user.get('status') == -2:
#             return response.json({
#                 '_success': False,
#                 'message': 'you do not have access'
#             })
#
#         if not user.get('scope') or not isinstance(user.get('scope'), list):
#             return response.json({
#                 '_success': False,
#                 'message': 'you do not have permissions'
#             })
#
#         user = UserSerializer(id=str(user['_id']), name=user['scope'])
#
#         if user:
#             auth.login_user(request, user)
#
#             return response.json({
#                 '_success': True,
#                 'redirect_url': '/profile/'
#             })
#
#         return response.json({
#             '_success': True
#         })
#
#
# class RegisterAPIView(HTTPMethodView):
#     async def post(self, request):
#         username = StrUtils.to_str(request.json.get('username'))
#         email = StrUtils.to_str(request.json.get('email'))
#         password = StrUtils.to_str(request.json.get('password'))
#         reply_password = StrUtils.to_str(request.json.get('reply_password'))
#
#         if username:
#             duplicate = await mongo.clients.find_one({'username': username, 'status': 0})
#             if duplicate:
#                 return response.json({
#                     '_success': False,
#                     'message': 'Duplicate: username'
#                 })
#         else:
#             return response.json({
#                 '_success': False,
#                 'message': 'Required param(s): username'
#             })
#
#         if email:
#             if not re.fullmatch(email_regex, email):
#                 return response.json({
#                     '_success': False,
#                     'message': 'Invalid email'
#                 })
#         else:
#             return response.json({
#                 '_success': False,
#                 'message': 'Required param(s): email'
#             })
#
#         if password:
#             if password == reply_password:
#                 passwd_hash = md5()
#                 passwd_hash.update(password.encode())
#                 password = passwd_hash.hexdigest()
#             else:
#                 return response.json({
#                     '_success': False,
#                     'message': 'Password does not match'
#                 })
#         else:
#             return response.json({
#                 '_success': False,
#                 'message': 'Required param(s): password'
#             })
#
#         inserted_id = await mongo.clients.insert_one({
#             'username': username,
#             'password': password,
#             'email': email,
#             'scope': ['client'],
#             'status': 0
#         })
#
#         if inserted_id:
#             user = UserSerializer(id=str(inserted_id.inserted_id), name=['client'])
#
#             if user:
#                 auth.login_user(request, user)
#                 return response.json({
#                     '_success': True,
#                     'redirect_url': '/profile/'
#                 })
#
#         return response.json({
#             '_success': False,
#             'message': 'Operation failed'
#         })
#
#
# class LogoutAPIView(BaseAPIView):
#     async def get(self, request, user):
#         auth.logout_user(request)
#         return response.redirect('/login/')
