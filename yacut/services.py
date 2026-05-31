from yacut import db
from .models import URLMap
from .utils import get_unique_short_id


class URLMapService:
    """Сервис для генерации и получения коротких ссылок."""

    @staticmethod
    def create_short_link(original, custom_id=None):
        """Генерация короткой ссылки."""
        if not custom_id:
            short = get_unique_short_id(db.session)
        else:
            if URLMap.query.filter_by(short=custom_id).first():
                raise ValueError(f'Имя "{custom_id}" уже занято.')
            short = custom_id
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_original_url(short_id):
        """Получает оригинальный URL по короткому идентификатору."""
        return URLMap.query.filter_by(short=short_id).first()