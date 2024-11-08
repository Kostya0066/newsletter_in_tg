# main.py

import tkinter as tk
from gui.main_window import TelegramMailerApp

def main():
    root = tk.Tk()
    app = TelegramMailerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
