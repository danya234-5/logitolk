import threading
from socket import *
from tkinter import Toplevel, Button, END
from customtkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("💬 Кольоровий чат з емодзі 🎨")
        self.geometry("700x500")
        self.minsize(600, 400)

        # === Бокове меню ===
        self.frame = CTkFrame(self, width=0)
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text='Ваше Ім`я:')
        self.label.pack(pady=10)

        self.entry = CTkEntry(self.frame)
        self.entry.pack(pady=5)

        self.save_btn = CTkButton(self.frame, text="💾 Зберегти нік", command=self.save_username)
        self.save_btn.pack(pady=10)

        # === Теми (8 кольорів) ===
        colors = ['Темна', 'Світла', 'Синя', 'Зелена', 'Червона', 'Фіолетова', 'Помаранчева', 'Рожева']
        self.label_theme = CTkOptionMenu(self.frame, values=colors, command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)

        # === Основна частина ===
        self.chat_frame = CTkFrame(self)
        self.chat_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.menu_show_speed = 20

        self.chat_text = CTkTextbox(self.chat_frame, state='disabled')
        self.chat_text.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        # === Нижня панель ===
        self.bottom_frame = CTkFrame(self.chat_frame)
        self.bottom_frame.pack(fill="x", pady=5)

        self.message_input = CTkEntry(self.bottom_frame, placeholder_text='Введіть повідомлення:')
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Кнопки
        self.emoji_button = CTkButton(self.bottom_frame, text="😊", width=40, command=self.open_emoji_window)
        self.emoji_button.pack(side="left", padx=(0, 5))

        self.send_button = CTkButton(self.bottom_frame, text='📨', width=40, command=self.send_message)
        self.send_button.pack(side="right")

        self.username = "В. Даніїл"

        # === Підключення до сервера ===
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("5.tcp.eu.ngrok.io", 13334))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався до чату!\n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"❌ Не вдалось підключитись: {e}")

    # === Меню ===
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀️')
        if self.is_show_menu:
            self.after(20, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶️')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    # === Зміна теми ===
    def change_theme(self, value):
        colors = {
            'Темна': ('dark', "#1e1e1e"),
            'Світла': ('light', "#ffffff"),
            'Синя': ('light', "#1e90ff"),
            'Зелена': ('light', "#32cd32"),
            'Червона': ('light', "#ff4040"),
            'Фіолетова': ('light', "#9932cc"),
            'Помаранчева': ('light', "#ff8c00"),
            'Рожева': ('light', "#ff69b4"),
        }
        theme, color = colors.get(value, ('light', "#ffffff"))
        set_appearance_mode(theme)
        self.configure(fg_color=color)

    # === Емодзі ===
    def open_emoji_window(self):
        emoji_window = Toplevel(self)
        emoji_window.title("Емодзі")
        emoji_window.geometry("280x280")

        emojis = ["😀", "😂", "😍", "😎", "🤔", "😢", "😡", "👍", "❤️", "🔥",
                  "🎉", "💡", "😇", "😴", "😅", "😜"]
        for e in emojis:
            btn = Button(emoji_window, text=e, font=("Arial", 14), width=4,
                         command=lambda emoji=e: self.insert_emoji(emoji, emoji_window))
            btn.pack(side="left", padx=3, pady=3)

    def insert_emoji(self, emoji_char, window):
        self.message_input.insert(END, emoji_char)
        window.destroy()

    # === Відправлення повідомлення ===
    def send_message(self):
        message = self.message_input.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_input.delete(0, END)

    # === Додавання тексту у вікно ===
    def add_message(self, text):
        self.chat_text.configure(state="normal")
        self.chat_text.insert(END, text + "\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see(END)

    # === Отримання повідомлень ===
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            self.add_message(f"{author}: {message}")
        else:
            self.add_message(line)

    # === Збереження імені ===
    def save_username(self):
        new_name = self.entry.get().strip()
        if new_name:
            old_name = self.username
            self.username = new_name
            try:
                msg = f"TEXT@{self.username}@[SYSTEM] {old_name} змінив імʼя на {self.username}\n"
                self.sock.send(msg.encode("utf-8"))
            except:
                pass
            self.add_message(f"✅ Нік змінено на {self.username}")

win = MainWindow()
win.mainloop()
