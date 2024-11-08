# gui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from telethon import TelegramClient, errors
from config.config import API_ID, API_HASH, SESSION_NAME
from utils.sender import send_message

class TelegramMailerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Mailer")
        self.root.geometry("500x400")
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.groups = []
        self.is_sending = False
        self.message = ""

        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}

        # Номер телефона
        self.phone_label = ttk.Label(self.root, text="Номер телефона (в формате +123456789):")
        self.phone_label.pack(**padding)
        self.phone_entry = ttk.Entry(self.root, width=40)
        self.phone_entry.pack(**padding)

        # Код из SMS
        self.code_label = ttk.Label(self.root, text="Код из SMS:")
        self.code_label.pack(**padding)
        self.code_entry = ttk.Entry(self.root, width=40)
        self.code_entry.pack(**padding)

        # Пароль (если включена двухфакторная аутентификация)
        self.password_label = ttk.Label(self.root, text="Пароль (если есть):")
        self.password_label.pack(**padding)
        self.password_entry = ttk.Entry(self.root, width=40, show="*")
        self.password_entry.pack(**padding)

        # Текст сообщения
        self.message_label = ttk.Label(self.root, text="Текст сообщения для рассылки:")
        self.message_label.pack(**padding)
        self.message_text = tk.Text(self.root, height=10, width=50)
        self.message_text.pack(**padding)

        # Кнопки
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.auth_button = ttk.Button(self.button_frame, text="Авторизоваться", command=self.authenticate)
        self.auth_button.grid(row=0, column=0, padx=5)

        self.start_button = ttk.Button(self.button_frame, text="Начать рассылку", command=self.start_sending, state='disabled')
        self.start_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Остановить рассылку", command=self.stop_sending, state='disabled')
        self.stop_button.grid(row=0, column=2, padx=5)

    def authenticate(self):
        phone = self.phone_entry.get().strip()
        code = self.code_entry.get().strip()
        password = self.password_entry.get().strip()

        if not phone:
            messagebox.showerror("Ошибка", "Пожалуйста, введите номер телефона.")
            return

        # Запуск авторизации в отдельном потоке
        threading.Thread(target=self.run_authentication, args=(phone, code, password), daemon=True).start()

    def run_authentication(self, phone, code, password):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.perform_authentication(phone, code, password))
        loop.close()

    async def perform_authentication(self, phone, code, password):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(phone)
                if code:
                    try:
                        await self.client.sign_in(phone, code)
                    except errors.SessionPasswordNeededError:
                        if password:
                            await self.client.sign_in(password=password)
                        else:
                            messagebox.showerror("Ошибка", "Требуется пароль для двухфакторной аутентификации.")
                            return
                else:
                    messagebox.showinfo("Информация", "Код был отправлен на ваш телефон.")
                    return

            self.groups = await self.get_groups()
            messagebox.showinfo("Успех", f"Авторизация успешна! Найдено сообществ: {len(self.groups)}")
            self.start_button.config(state='normal')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка авторизации: {e}")
        finally:
            await self.client.disconnect()

    async def get_groups(self):
        await self.client.connect()
        dialogs = await self.client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
        await self.client.disconnect()
        return groups

    def start_sending(self):
        self.message = self.message_text.get("1.0", tk.END).strip()
        if not self.message:
            messagebox.showerror("Ошибка", "Пожалуйста, введите текст сообщения.")
            return
        self.is_sending = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        threading.Thread(target=self.run_sending, daemon=True).start()

    def run_sending(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.perform_sending())
        loop.close()

    async def perform_sending(self):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                messagebox.showerror("Ошибка", "Необходимо авторизоваться перед рассылкой.")
                return
            while self.is_sending:
                for group in self.groups:
                    if not self.is_sending:
                        break
                    try:
                        await send_message(self.client, group, self.message)
                    except Exception as e:
                        print(f"Ошибка при отправке в {group.title}: {e}")
                    await asyncio.sleep(1)  # Небольшая задержка между сообщениями

                if self.is_sending:
                    print("Жду 15 минут перед следующей рассылкой...")
                    await asyncio.sleep(15 * 60)  # 15 минут
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при рассылке: {e}")
        finally:
            await self.client.disconnect()
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            messagebox.showinfo("Информация", "Рассылка завершена.")

    def stop_sending(self):
        self.is_sending = False
        self.stop_button.config(state='disabled')
        self.start_button.config(state='normal')
        print("Рассылка остановлена пользователем.")

