from bson import ObjectId

from core.db import mongo
from core.handlers import BaseAPIView


class EmployeesView(BaseAPIView):
    template_name = 'adminn/employees.html'

    async def get(self, request, user):
        context = dict()
        filter_obj = {
            'status': 0
        }
        context['roles'] = await mongo.roles.find({'status': 0}).to_list(length=None)
        data = []
        async for employee in mongo.employees.find(filter_obj).sort('_id', -1):
            if employee.get('role_id') and ObjectId.is_valid(employee['role_id']):
                employee['role_id'] = await mongo.roles.find_one({'_id': ObjectId(employee['role_id'])})
            else:
                employee['role_id'] = {
                    'title': None
                }
            data.append(employee)

        context['data'] = data

        # CURRENT USER
        context['user'] = await mongo.users.find_one({'_id': ObjectId(user.id)})

        return self.render_template(request=request, **context)
