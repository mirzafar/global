from sanic import Blueprint

from .list import EmployeesView
from .salary import SalaryView

__all__ = ['employees_bp']

employees_bp = Blueprint('employees')

employees_bp.add_route(EmployeesView.as_view(), '/employees/', name='employees')
employees_bp.add_route(SalaryView.as_view(), '/employees/salary/', name='salary')
