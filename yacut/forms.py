from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import (
    DataRequired, Length, Regexp, ValidationError, URL, Optional
)
from flask_wtf.file import FileField, FileRequired, FileAllowed

from .models import URLMap
from .constants import MAX_ORIGINAL_LENGTH, MAX_SHORT_LENGTH


RESERVED_SHORT_ID = 'files'


class URLMapForm(FlaskForm):
    """Форма для создания короткой ссылки."""
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректный URL'),
            Length(
                max=MAX_ORIGINAL_LENGTH,
                message='Ссылка не может быть длиннее 256 символов'
            )
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(
                max=MAX_SHORT_LENGTH,
                message='Короткая ссылка не может быть длиннее 16 символов'
            ),
            Optional(),
            Regexp(
                r'^[a-zA-Z0-9]+$',
                message=(
                    'Короткая ссылка может содержать только '
                    'латинские буквы и цифры'
                )
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        """Проверка кастомного короткого идентификатора."""
        if field.data:
            if field.data.strip() != field.data:
                raise ValidationError(
                    'Короткая ссылка не может содержать пробелы'
                )
            if field.data == RESERVED_SHORT_ID:
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if URLMap.query.filter_by(short=field.data).first():
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс Диск."""
    files = FileField(
        'Файлы',
        validators=[
            FileRequired(message='Выберите файлы для загрузки'),
            FileAllowed(
                ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'],
                message='Недопустимый тип файла')
        ],
        render_kw={'multiple': True}
    )
    submit = SubmitField('Загрузить')
