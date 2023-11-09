from sanic import Blueprint

from .receipts import ReceiptsView

__all__ = ['receipts_bp']

receipts_bp = Blueprint('receipts')

receipts_bp.add_route(ReceiptsView.as_view(), '/order/receipts/', name='order.receipts')
