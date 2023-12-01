from sanic import Blueprint

from admin.api.companies.item import CompaniesItemView
from admin.api.companies.list import CompaniesListView
from admin.api.companies.template import CompaniesTemplateView

companies_bp = Blueprint('companies', url_prefix='/companies')

companies_bp.add_route(CompaniesTemplateView.as_view(), '/template/')
companies_bp.add_route(CompaniesListView.as_view(), '/list/')
companies_bp.add_route(CompaniesItemView.as_view(), '/<company_id>/item/')
