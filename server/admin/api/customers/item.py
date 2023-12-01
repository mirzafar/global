from datetime import datetime

from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from core.hasher import password_to_hash
from utils.ints import IntUtils
from utils.strs import StrUtils


class CustomersItemView(BaseAPIView):

    async def get(self, request, user, customer_id):
        customer_id = IntUtils.to_int(customer_id)
        if not customer_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): customer_id'
            })

        customer = dict(await db.fetchrow(
            '''
            SELECT *
            FROM public.customers
            WHERE id = $1
            ''',
            customer_id
        ) or {})

        return response.json({
            'data': customer
        }, dumps=encoder.encode)

    async def post(self, request, user, customer_id):
        first_name = StrUtils.to_str(request.json.get('first_name'))
        last_name = StrUtils.to_str(request.json.get('last_name'))
        middle_name = StrUtils.to_str(request.json.get('middle_name'))
        username = StrUtils.to_str(request.json.get('username'))
        password = StrUtils.to_str(request.json.get('password'))
        reply_password = StrUtils.to_str(request.json.get('reply_password'))
        photo = StrUtils.to_str(request.json.get('photo'))
        phone_number = StrUtils.to_str(request.json.get('phone_number'))
        birthday = StrUtils.to_str(request.json.get('birthday'))
        wp_number = StrUtils.to_str(request.json.get('wp_number'))

        if not first_name or not last_name:
            return response.json({
                '_success': False,
                'message': 'Required param(s): first_name or last_name'
            })

        if password:
            if password == reply_password:
                password = password_to_hash(password)
            else:
                return response.json({
                    '_success': False,
                    'message': 'Password does not match'
                })

        if customer_id == 'new':
            if username:
                duplicate = await db.fetchrow(
                    '''
                    SELECT *
                    FROM public.customers
                    WHERE username = $1
                    ''',
                    username
                )
                if duplicate:
                    return response.json({
                        '_success': False,
                        'message': 'Duplicate: username'
                    })

            data = await db.fetchrow(
                '''
                INSERT INTO public.customers
                (last_name, first_name, middle_name, password, username, photo, birthday, phone_number, wp_number)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                ''',
                last_name,
                first_name,
                middle_name,
                password,
                username,
                photo,
                datetime.strptime(birthday, '%Y-%m-%d') if birthday else None,
                phone_number,
                wp_number,
            )

            if data:
                return response.json({
                    '_success': True,
                    'visit': dict(data)
                }, dumps=encoder.encode)

            else:
                return response.json({
                    '_success': False,
                    'message': 'Operation failed'
                })

        customer_id = IntUtils.to_int(customer_id)
        if not customer_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): customer_id'
            })

        customer = await db.fetchrow(
            '''
            SELECT *
            FROM public.customers
            WHERE id = $1
            ''',
            customer_id
        )

        if not password:
            password = customer['password']

        data = await db.fetchrow(
            '''
            UPDATE public.customers
            SET 
                last_name = $2, 
                first_name = $3, 
                middle_name = $4,
                password = $5,
                username = $6,
                photo = $7,
                phone_number = $8,
                wp_number = $9,
                birthday = $10
            WHERE id = $1
            RETURNING *
            ''',
            customer_id,
            last_name,
            first_name,
            middle_name,
            password,
            username,
            photo,
            phone_number,
            wp_number,
            datetime.strptime(birthday, '%Y-%m-%d') if birthday else None,
        )

        if not data:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True,
            'data': dict(data)
        }, dumps=encoder.encode)

    async def delete(self, request, user, customer_id):
        customer_id = IntUtils.to_int(customer_id)
        if not customer_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): customer_id'
            })

        data = await db.fetchrow(
            '''
            UPDATE public.customers
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            customer_id,
        )

        if not data:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })
