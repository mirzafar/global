from sanic import Blueprint

from admin.api.customers.item import CustomersItemView
from admin.api.customers.list import CustomersListView
from admin.api.customers.templates import CustomersTemplateView, CustomersCreateTemplateView, CustomersItemTemplateView

__all__ = ['customers_bp']

customers_bp = Blueprint('customers', url_prefix='/customers')

customers_bp.add_route(CustomersListView.as_view(), '/list/')
customers_bp.add_route(CustomersTemplateView.as_view(), '/template/')
customers_bp.add_route(CustomersItemTemplateView.as_view(), '/<customer_id>/template/')
customers_bp.add_route(CustomersItemView.as_view(), '/<customer_id>/item/')
customers_bp.add_route(CustomersCreateTemplateView.as_view(), '/<customer_id>/create/')
