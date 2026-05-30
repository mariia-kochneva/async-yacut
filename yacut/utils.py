import random
import string

from .models import URLMap


def get_unique_short_id(db_session, length=6, max_attempts=100):
    """Генерирует уникальный короткий идентификатор."""
    for _ in range(max_attempts):
        short_id = ''.join(random.choices(
            string.ascii_letters + string.digits,
            k=length
        ))
        if not db_session.query(URLMap).filter_by(short=short_id).first():
            return short_id
    raise RuntimeError(
        'Не удалось сгенерировать уникальный короткий идентификатор'
    )
