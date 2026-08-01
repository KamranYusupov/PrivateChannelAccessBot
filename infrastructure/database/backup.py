import os
import gzip
import shutil
import tempfile
import subprocess
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Generator

import loguru
from django.conf import settings


def create_postgres_backup() -> Path:
    """
    Создает дамп базы данных PostgreSQL и сжимает его в .gz архив.
    """
    timestamp = datetime.now().strftime('%H-%M_%Y-%m-%d')

    sql_path = Path(tempfile.gettempdir()) / f'backup_{timestamp}.sql'
    gz_path = sql_path.with_suffix('.sql.gz')

    env = os.environ.copy()
    env['PGPASSWORD'] = settings.POSTGRES_PASSWORD

    result = subprocess.run(
        [
            'pg_dump',
            '-h', settings.POSTGRES_HOST,
            '-p', str(settings.POSTGRES_PORT),
            '-U', settings.POSTGRES_USER,
            '-d', settings.POSTGRES_DB,
            '-f', str(sql_path),
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise RuntimeError(f'pg_dump failed: {result.stderr.decode()}')

    with open(sql_path, 'rb') as src:
        with gzip.open(gz_path, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    sql_path.unlink()

    return gz_path


@contextmanager
def postgres_backup_context() -> Generator[Path, None, None]:
    """
    Контекстный менеджер. Создает бэкап и ГАРАНТИРОВАННО удаляет его
    после выхода из блока with.
    """
    gz_backup_path = create_postgres_backup()

    try:
        # Отдаем путь к файлу в блок with
        yield gz_backup_path
    finally:
        if gz_backup_path.exists():
            gz_backup_path.unlink()
            loguru.logger.debug(f'Temporary backup file deleted: {gz_backup_path}')