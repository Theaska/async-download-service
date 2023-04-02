import asyncio
import logging
import os
from aiohttp import web
import aiofiles

from argparser import args


logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger('server')


BATCH_SIZE = args.batch_size
BASE_DIR = os.getcwd()
PHOTOS_DIR = os.path.join(BASE_DIR, args.photos_dir)
ZIP_NAME = 'archive.zip'
ENABLE_LOGGING = args.enable_logging
ENABLE_DELAY = args.enable_delay
STDOUT = 1


def log(message: str, level: int = logging.INFO):
    if ENABLE_LOGGING:
        logger.log(level, message)


async def archive(request: web.Request):
    archive_hash = request.match_info['archive_hash']
    cmd = ['zip', '-r', '-', '.', '|', f'>&{STDOUT}']
    photo_path = os.path.join(PHOTOS_DIR, archive_hash)

    if not os.path.exists(photo_path):
        raise web.HTTPNotFound(text='Архив не существует или был удален')

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=photo_path
    )
    response = web.StreamResponse()
    response.headers['content-disposition'] = f'attachment; filename={ZIP_NAME}'
    await response.prepare(request)

    try:
        while True:
            stdout = await process.stdout.read(BATCH_SIZE)
            log('Read chunk ...')

            await response.write(stdout)
            if ENABLE_DELAY:
                await asyncio.sleep(1)

            log('Finish read chunk ...')

            if process.stdout.at_eof():
                log('Get EOF, finish.')
                return response
    finally:
        if process.returncode is None:
            log('Download was interrupted')
            process.kill()
            await process.communicate()


async def handle_index_page(request: web.Request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
