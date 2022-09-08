import getopt
import importlib
import logging
import multiprocessing
import sys
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from sanic import Sanic

from entity import BotConfig
from init import init_logger
from utils import FileUtils

app = Sanic('bililive-uploader')
importlib.import_module('server.route')  # import it to register routes
importlib.import_module('server.tasks')  # import it to register tasks


@app.main_process_start
def init(*_):
    cpu_count = multiprocessing.cpu_count()
    app.ctx.bot_config = bot_config
    app.ctx.process_pool = ThreadPoolExecutor(max_workers=min(cpu_count, bot_config.workers))
    app.ctx.upload_queue = Queue()
    app.config.TIME_CACHE_PATH = './cache/time.json'
    app.config.VIDEO_CACHE_PATH = './cache/videos.json'


@app.on_request
def refresh_config(*_):
    app.ctx.global_config = BotConfig(work_dir)


if __name__ == '__main__':
    try:
        options, args = getopt.getopt(sys.argv[1:], 'w:', ['work-dir='])
        for option, value in options:
            if option in ('-w', '--work-dir'):
                work_dir = value
                break
        else:
            raise getopt.GetoptError('work dir is not specified')
    except getopt.GetoptError as e:
        logging.critical(e)
        sys.exit(2)
    FileUtils.deleteFolder('./cache')
    init_logger(work_dir)
    bot_config = BotConfig(work_dir)
    app.run(host='0.0.0.0', port=bot_config.port, auto_reload=True,
            debug=False, access_log=False)