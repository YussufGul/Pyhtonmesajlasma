import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyaudio
import wave
HOST = '0.0.0.0'  
PORT = 8080        
clients = []
nicknames = []
is_recording = False
frames = []
def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            clients.remove(client)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
            update_chat_box(message.decode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f'{nickname} ayrıldı!'.encode('utf-8'))
            update_chat_box(f'{nickname} ayrıldı!')
            break

def receive():
    while True:
        client, address = server.accept()
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        broadcast(f'{nickname} sohbete katıldı!'.encode('utf-8'))
        update_chat_box(f'{nickname} sohbete katıldı!')
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

def update_chat_box(message):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, message + "\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def start_server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    update_chat_box("Sohbet başlatıldı...")

def record_audio():
    global is_recording, frames
    is_recording = True
    frames = []
    chunk = 1024  
    format = pyaudio.paInt16  
    channels = 1  
    rate = 44100  
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    while is_recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

def stop_recording_and_send():
    global is_recording
    is_recording = False

    filename = "recorded_audio.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

    listen_and_send(filename)

def listen_and_send(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)

    try:
        message = recognizer.recognize_google(audio_data, language="tr-TR")
        full_message = f'Sunucu: {message}'
        broadcast(full_message.encode('utf-8'))
        update_chat_box(full_message)
    except sr.UnknownValueError:
        print("Ses anlaşılamadı.")
    except sr.RequestError as e:
        print(f"Ses tanıma servisine ulaşılamadı; {e}")

def send_message():
    message = message_entry.get()
    if message:
        full_message = f'Sunucu: {message}'
        broadcast(full_message.encode('utf-8'))
        update_chat_box(full_message)
        message_entry.delete(0, tk.END)

def start_recording_thread():
    threading.Thread(target=record_audio).start()

def start_server_gui():
    global chat_box, message_entry

    window = tk.Tk()
    window.title("Sunucu")
    window.configure(bg='#ADD8E6')

    chat_box = scrolledtext.ScrolledText(window, width=50, height=20, bg='#E0FFFF', fg='#000000')
    chat_box.config(state=tk.DISABLED)
    chat_box.grid(row=0, column=0, padx=10, pady=10)

    message_entry = tk.Entry(window, width=40, bg='#F0F8FF')
    message_entry.grid(row=1, column=0, padx=10, pady=10)

    send_button = tk.Button(window, text="Gönder", command=send_message, bg='#87CEFA')
    send_button.grid(row=1, column=1, padx=10, pady=10)

    record_button = tk.Button(window, text="Ses Kaydet", command=start_recording_thread, bg='#FFA07A')
    record_button.grid(row=1, column=2, padx=10, pady=10)

    stop_button = tk.Button(window, text="Kaydı Bitir ve Gönder", command=stop_recording_and_send, bg='#FF4500')
    stop_button.grid(row=1, column=3, padx=10, pady=10)

    start_server()
    window.mainloop()

start_server_gui()