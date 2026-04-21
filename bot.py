import asyncio
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── Health-check сервер (нужен для Render + UptimeRobot) ─────────────────────

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Отключаем лишние логи HTTP-запросов


def run_health_server():
    """Запускает лёгкий HTTP-сервер на порту 10000 (порт по умолчанию на Render)."""
    port = 10000
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health-check сервер запущен на порту {port}")
    server.serve_forever()


# ── Основной бот ──────────────────────────────────────────────────────────────

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    logger.info("Бот запущен (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем health-сервер в отдельном потоке
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Запускаем бота
    asyncio.run(main())
