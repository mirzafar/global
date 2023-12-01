from sanic import response

from core.db import db
from core.encoder import encoder
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class CompaniesItemView(BaseAPIView):

    async def get(self, request, user, company_id):
        company_id = IntUtils.to_int(company_id)
        if not company_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): company_id'
            })

        company = dict(await db.fetchrow(
            '''
            SELECT *
            FROM public.companies
            WHERE id = $1
            ''',
            company_id
        ) or {})

        return response.json({
            'company': company
        }, dumps=encoder.encode)

    async def post(self, request, user, company_id):
        title = StrUtils.to_str(request.json.get('title'))
        if not title:
            return response.json({
                '_success': False,
                'message': 'Required param(s): title'
            })

        description = StrUtils.to_str(request.json.get('description'))
        address = StrUtils.to_str(request.json.get('address'))
        phone_number = StrUtils.to_str(request.json.get('phone_number'))
        wp_number = StrUtils.to_str(request.json.get('wp_number'))

        if company_id == 'new':
            data = await db.fetchrow(
                '''
                INSERT INTO public.companies(title, description, address, phone_number, wp_number)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                ''',
                title,
                description,
                address,
                phone_number,
                wp_number,
            )

            if data:
                return response.json({
                    '_success': True,
                    'data': dict(data)
                }, dumps=encoder.encode)

            else:
                return response.json({
                    '_success': False,
                    'message': 'Operation failed'
                })

        company_id = IntUtils.to_int(company_id)
        if not company_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): category_id'
            })

        data = await db.fetchrow(
            '''
            UPDATE public.companies
            SET title = $2, description = $3, address = $4, phone_number = $5, wp_number = $6
            WHERE id = $1
            RETURNING *
            ''',
            company_id,
            title,
            description,
            address,
            phone_number,
            wp_number,
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

    async def delete(self, request, user, company_id):
        company_id = IntUtils.to_int(company_id)
        if not company_id:
            return response.json({
                '_success': False,
                'message': 'Required param(s): company_id'
            })

        data = await db.fetchrow(
            '''
            UPDATE public.companies
            SET status = -1
            WHERE id = $1
            RETURNING *
            ''',
            company_id,
        )

        if not data:
            return response.json({
                '_success': False,
                'message': 'Operation failed'
            })

        return response.json({
            '_success': True
        })
