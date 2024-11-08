# utils/sender.py

from telethon import TelegramClient, errors
import asyncio

async def send_message(client: TelegramClient, group, message: str):
    """
    Отправляет сообщение в указанное сообщество.

    :param client: Экземпляр TelegramClient
    :param group: Объект группы или канала
    :param message: Текст сообщения для отправки
    """
    try:
        await client.send_message(group, message)
        print(f"Сообщение отправлено в {group.title}")
    except errors.FloodWaitError as e:
        print(f"Flood wait: нужно подождать {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        await send_message(client, group, message)  # Повторная попытка
    except Exception as e:
        print(f"Не удалось отправить сообщение в {group.title}: {e}")

