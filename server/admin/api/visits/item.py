from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.ints import IntUtils
from utils.strs import StrUtils


class VisitsItemView(BaseAPIView):

    async def get(self, request, user, visit_id):
        visit_id = IntUtils.to_int(visit_id)
        if not visit_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): visit_id'
            })

        visit = dict(await db.fetchrow(
            '''
            SELECT *
            FROM public.visits
            WHERE id = $1
            ''',
            visit_id
        ) or {})

        return response.json({
            'visit': visit
        }, dumps=encoder.encode)

    async def post(self, request, user, visit_id):
        customer_id = IntUtils.to_int(request.json.get('customer_id'))
        user_id = IntUtils.to_int(request.json.get('user_id'))
        phone_number = StrUtils.to_str(request.json.get('phone_number'))
        message = StrUtils.to_str(request.json.get('message'))
        reason = StrUtils.to_str(request.json.get('reason'))
        category_id = IntUtils.to_int(request.json.get('category_id'))
        price = BoolUtils.to_bool(request.json.get('price'))
        total_price = BoolUtils.to_bool(request.json.get('total_price'))
        discount = IntUtils.to_int(request.json.get('discount'))

        if visit_id == 'new':
            visit = await db.fetchrow(
                '''
                INSERT INTO public.visits(customer_id, user_id, phone_number, message, category_id, price, discount, total_price, reason)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                ''',
                customer_id,
                user_id,
                phone_number,
                message,
                category_id,
                price,
                discount,
                total_price,
                reason,
            )

            if visit:
                return response.json({
                    '_success': True,
                    'visit': dict(visit)
                }, dumps=encoder.encode)

            else:
                return response.json({
                    '_success': False,
                    'message': 'Operation failed'
                })

        visit_id = IntUtils.to_int(visit_id)
        if not visit_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): visit_id'
            })

        visit = await db.fetchrow(
            '''
            UPDATE public.visits
            SET 
                customer_id = $2, 
                user_id = $3, 
                phone_number = $4,
                message = $5,
                category_id = $6,
                price = $7,
                discount = $8,
                total_price = $9,
                reason = $10
            WHERE id = $1
            RETURNING *
            ''',
            visit_id,
            customer_id,
            user_id,
            phone_number,
            message,
            category_id,
            price,
            discount,
            total_price,
            reason,
        )

        if not visit:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True,
            'visit': dict(visit)
        }, dumps=encoder.encode)

    async def delete(self, request, user, visit_id):
        visit_id = IntUtils.to_int(visit_id)
        if not visit_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): visit_id'
            })

        visit = await db.fetchrow(
            '''
            UPDATE public.visits
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            visit_id,
        )

        if not visit:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })
