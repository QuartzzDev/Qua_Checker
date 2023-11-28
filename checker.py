# QuartzzDev - Discord : quartzz.dll

import time
import os
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
import threading

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.conn = sqlite3.connect('file_changes.db')
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                file_loc TEXT,
                event_type TEXT,
                event_time TEXT
            )
        ''')
        self.conn.commit()

    def on_created(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'created':
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_loc = os.path.dirname(file_path)
            event_time = time.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f'Dosya oluşturuldu: {file_path}')
            with self.lock, sqlite3.connect('file_changes.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_changes (file_name, file_loc, event_type, event_time)
                    VALUES (?, ?, ?, ?)
                ''', (file_name, file_loc, 'created', event_time))
                conn.commit()

            send_notification('Qua Checker V1.0', f'Dosya oluşturuldu: {file_name}')

    def on_modified(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'modified':
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_loc = os.path.dirname(file_path)
            event_time = time.strftime('%Y-%m-%d %H:%M:%S')

            print(f'Dosya değiştirildi: {file_path}')
            with self.lock, sqlite3.connect('file_changes.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_changes (file_name, file_loc, event_type, event_time)
                    VALUES (?, ?, ?, ?)
                ''', (file_name, file_loc, 'modified', event_time))
                conn.commit()

            send_notification('Qua Checker V1.0', f'Dosya değiştirildi: {file_name}')

    def on_deleted(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'deleted':
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_loc = os.path.dirname(file_path)
            event_time = time.strftime('%Y-%m-%d %H:%M:%S')

            print(f'Dosya silindi: {file_path}')
            with self.lock, sqlite3.connect('file_changes.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_changes (file_name, file_loc, event_type, event_time)
                    VALUES (?, ?, ?, ?)
                ''', (file_name, file_loc, 'deleted', event_time))
                conn.commit()

            send_notification('Qua Checker V1.0', f'Dosya silindi: {file_name}')

    def __del__(self):
        self.conn.close()

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Dosya İzleyici',
        app_icon=None,
        timeout=10,
    )

if __name__ == "__main__":
    paths = [".", "."]    # Please add here your directories
    event_handler = MyHandler()
    
    observers = []
    for path in paths:
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        observers.append(observer)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
