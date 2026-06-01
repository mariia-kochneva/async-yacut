import re
import random
import string

from yacut import db
from .models import URLMap
from .constants import (
    DEFAULT_SHORT_ID_LENGTH,
    MAX_GENERATION_ATTEMPTS,
    MAX_SHORT_LENGTH,
    SHORT_ID_PATTERN,
    RESERVED_SHORT_ID,
    INVALID_SHORT_ID_MSG
)


class URLMapService:
    """Сервис для генерации и получения коротких ссылок."""

    @staticmethod
    def _generate_unique_short_id():
        """Генерирует уникальный короткий идентификатор."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short_id = ''.join(random.choices(
                string.ascii_letters + string.digits,
                k=DEFAULT_SHORT_ID_LENGTH
            ))
            if not URLMap.query.filter_by(short=short_id).first():
                return short_id
        raise RuntimeError(
            'Не удалось сгенерировать уникальный короткий идентификатор'
        )

    @staticmethod
    def _validate_custom_id(custom_id):
        """Валидация пользовательского короткого идентификатора."""
        if len(custom_id) > MAX_SHORT_LENGTH:
            raise ValueError(INVALID_SHORT_ID_MSG)
        if not re.match(SHORT_ID_PATTERN, custom_id):
            raise ValueError(INVALID_SHORT_ID_MSG)
        if custom_id == RESERVED_SHORT_ID:
            raise ValueError(INVALID_SHORT_ID_MSG)

    @staticmethod
    def create_short_link(original, custom_id=None):
        """Генерация короткой ссылки."""
        if not custom_id:
            short = URLMapService._generate_unique_short_id()
        else:
            URLMapService._validate_custom_id(custom_id)
            if URLMap.query.filter_by(short=custom_id).first():
                raise ValueError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            short = custom_id

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_original_url(short_id):
        """Получает оригинальный URL по короткому идентификатору."""
        return URLMap.query.filter_by(short=short_id).first()
