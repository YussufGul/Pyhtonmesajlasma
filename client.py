import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

HOST = 'İpADRESİNİGİR'  
PORT = 8080        

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nickname = "" 

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, message + "\n")
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)
        except:
            messagebox.showerror("Hata", "Sunucu ile bağlantı kesildi!")
            client.close()
            break

def send_message():
    message = message_entry.get()
    if message:
        print(f'Gönderilen Mesaj: {message}')
        client.send(f'{nickname}: {message}'.encode('utf-8'))
        message_entry.delete(0, tk.END)

def start_client_gui():
    global chat_box, message_entry

    window = tk.Tk()
    window.title("İstemci")
    window.configure(bg='#ADD8E6')

    chat_box = scrolledtext.ScrolledText(window, width=50, height=20, bg='#E0FFFF', fg='#000000')
    chat_box.config(state=tk.DISABLED)
    chat_box.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    message_entry = tk.Entry(window, width=40, bg='#F0F8FF')
    message_entry.grid(row=1, column=0, padx=10, pady=10)

    send_button = tk.Button(window, text="Gönder", command=send_message, bg='#87CEFA')
    send_button.grid(row=1, column=1, padx=10, pady=10)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    window.mainloop()

def ask_nickname():
    def submit_nickname():
        global nickname
        nickname = nickname_entry.get()
        if nickname:
            client.send(nickname.encode('utf-8'))
            nickname_window.destroy()
            start_client_gui()

    nickname_window = tk.Tk()
    nickname_window.title("Kullanıcı Adı")
    nickname_window.configure(bg='#ADD8E6')

    tk.Label(nickname_window, text="Lütfen isminizi girin:", bg='#ADD8E6', font=("Arial", 12)).pack(pady=10)

    nickname_entry = tk.Entry(nickname_window, width=30, bg='#F0F8FF')
    nickname_entry.pack(pady=10)

    submit_button = tk.Button(nickname_window, text="Tamam", command=submit_nickname, bg='#87CEFA')
    submit_button.pack(pady=10)

    nickname_window.mainloop()

ask_nickname()
