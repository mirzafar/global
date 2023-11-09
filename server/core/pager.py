from typing import Optional

from utils.ints import IntUtils


class Pager:
    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 20

    page = DEFAULT_PAGE
    limit = DEFAULT_LIMIT

    _offset = None
    _query = None

    def set_page(self, page, default=DEFAULT_PAGE, minimum=1, maximum=None) -> 'Pager':
        self.page = self._sanitize(
            value=page,
            default=default,
            minimum=minimum,
            maximum=maximum
        )
        return self

    def reset_page(self) -> 'Pager':
        self.page = None
        return self

    def set_offset(self, offset, default=0, minimum=0, maximum=None) -> 'Pager':
        self._offset = self._sanitize(
            value=offset,
            default=default,
            minimum=minimum,
            maximum=maximum
        )
        return self

    def reset_offset(self) -> 'Pager':
        self._offset = None
        return self

    def set_limit(self, limit, default=DEFAULT_LIMIT, minimum=1, maximum=1000) -> 'Pager':
        self.limit = self._sanitize(
            value=limit,
            default=default,
            minimum=minimum,
            maximum=maximum
        )
        return self

    def reset_limit(self) -> 'Pager':
        self.limit = None
        return self

    @classmethod
    def _sanitize(cls, value, default, minimum, maximum) -> int:
        value = IntUtils.to_int(value)
        if value:
            if isinstance(minimum, int) and minimum > value:
                return minimum
            elif isinstance(maximum, int) and maximum < value:
                return maximum
            else:
                return value
        else:
            return default

    @property
    def offset(self) -> int:
        if self._offset is None:
            if self.page and self.limit:
                self._offset = (self.page - 1) * self.limit
            else:
                return 0
        return self._offset

    def as_query(self) -> Optional[str]:
        if self._query is None:
            offset, limit = self.offset, self.limit
            if isinstance(offset, int) and limit:
                self._query = f'LIMIT {limit} OFFSET {offset}'
        return self._query or ''

    def dict(self) -> dict:
        if self.page and self.limit:
            return {
                'page': self.page,
                'offset': self.offset,
                'limit': self.limit
            }
        return {}

    def next_page(self, total) -> int:
        return self.page + 1 if (self.page * self.limit) < total else self.page

    def prev_page(self) -> int:
        return self.page - 1 if self.page > 1 else self.page
