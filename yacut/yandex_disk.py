from flask import current_app


async def get_download_link(session, disk_path):
    """Асинхронное получение ссылки на скачивание."""
    API_HOST = 'https://cloud-api.yandex.net/v1/disk/resources/download'
    headers = {
        'Authorization': f'OAuth {current_app.config["DISK_TOKEN"]}',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    params = {'path': disk_path}
    async with session.get(
        API_HOST, headers=headers, params=params
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return data['href']


async def get_upload_url(session, disk_path):
    """Получение URL для загрузки файла."""
    API_HOST = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': f'OAuth {current_app.config["DISK_TOKEN"]}'}
    params = {'path': disk_path, 'overwrite': 'true'}
    async with session.get(
        API_HOST, headers=headers, params=params
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return data['href']


async def upload_file_to_yandex(session, file_data, disk_path):
    """Загрузка файла на Яндекс.Диск."""
    upload_url = await get_upload_url(session, disk_path)
    async with session.put(upload_url, data=file_data) as response:
        response.raise_for_status()
    return True