import asyncio
import aiohttp
import time

from werkzeug.utils import secure_filename
from flask import render_template, redirect, flash, request

from yacut import db, app
from yacut.models import URLMap
from yacut.forms import URLMapForm, FileUploadForm
from yacut.utils import get_unique_short_id
from yacut.yandex_disk import (
    get_download_link,
    upload_file_to_yandex
)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница - создание коротких ссылок."""
    form = URLMapForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data
        if not custom_id:
            short = get_unique_short_id(db.session)
        else:
            short = custom_id
        url_map = URLMap(
            original=original,
            short=short
        )
        db.session.add(url_map)
        db.session.commit()
        short_url = request.host_url + short
        flash(f'Короткая ссылка: {short_url}', 'success')
        return render_template('index.html', form=form, short_url=short_url)
    return render_template('index.html', form=form)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route('/<string:short_id>')
def redirect_to_url(short_id):
    """Редирект по короткой ссылке."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    if url_map.original.startswith(('app:/', 'disk:/')):
        async def fetch():
            async with aiohttp.ClientSession() as session:
                return await get_download_link(session, url_map.original)
        download_url = run_async(fetch())
        return redirect(download_url)
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files_page():
    """Страница загрузки файлов на Яндекс.Диск."""
    form = FileUploadForm()
    uploaded_files = []
    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not isinstance(files, list):
            files = [files]
        files = [f for f in files if f and f.filename]
        if len(files) == 0:
            flash('Выберите файлы для загрузки', 'danger')
            return render_template(
                'files.html', form=form, uploaded_files=uploaded_files
            )
        results = run_async(upload_files(files))
        for result in results:
            if 'error' in result:
                flash(
                    f'Ошибка загрузки {result["filename"]}: {result["error"]}',
                    'danger'
                )
            else:
                short_url = request.host_url + result['short_id']
                flash(
                    f'Файл {result["filename"]} загружен! Короткая '
                    f'ссылка: {short_url}', 'success'
                )
                uploaded_files.append({
                    'filename': result['filename'],
                    'short_url': short_url
                })
        return render_template(
            'files.html', form=form, uploaded_files=uploaded_files
        )
    return render_template(
        'files.html', form=form, uploaded_files=uploaded_files
    )


async def upload_files(files):
    """Загрузка нескольких файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, file in enumerate(files):
            task = upload_one_file(session, file, i)
            tasks.append(task)
        return await asyncio.gather(*tasks)


async def upload_one_file(session, file, index):
    """Загрузка файла на Яндекс.Диск."""
    if isinstance(file, bytes):
        display_name = f"картинка {index + 1}.png"
        safe_name = secure_filename(display_name)
        if not safe_name:
            safe_name = f"file_{int(time.time())}_{index}"
        filename = safe_name
        file_data = file
    else:
        display_name = file.filename
        safe_name = secure_filename(file.filename)
        if not safe_name:
            safe_name = f"file_{int(time.time())}_{index}"
        filename = safe_name
        file_data = file.read()
    disk_path = 'app:/' + filename
    try:
        await upload_file_to_yandex(session, file_data, disk_path)
        await get_download_link(session, disk_path)
        with app.app_context():
            short_id = get_unique_short_id(db.session)
            url_map = URLMap(original=disk_path, short=short_id)
            db.session.add(url_map)
            db.session.commit()
        return {
            'filename': display_name,
            'short_id': short_id,
        }
    except Exception as e:
        return {
            'filename': display_name,
            'error': str(e)
        }