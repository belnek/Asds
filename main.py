import os
import logging
from datetime import datetime
from time import sleep
import ctypes
import json
import time
import re
import psutil

from colorama import Fore
from telethon.sync import TelegramClient, errors
from telethon.errors.common import InvalidBufferError
from telethon.errors import SessionPasswordNeededError

log_file_path = 'errors.log'
if os.path.exists(log_file_path):
    open(log_file_path, 'w').close()

def create_proxy_file(filename='proxy.txt'):
    # Создание пустого файла proxy.txt, если его еще нет
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            pass 

logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def set_console_title(new_title):
    ctypes.windll.kernel32.SetConsoleTitleW(new_title)

def print_success(message):
    print(f"{message}")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

new_title = "TD"
#set_console_title(new_title)

logo = f"""                              
             ____  ____  ____  ___  ____  __   
            (  _ \( ___)(  _ \/ __)(_  _)(  )  
             )___/ )__)  )   /\__ \ _)(_  )(__ 
            (__)  (____)(_)\_)(___/(____)(____)
                
            Version [2]
            Разработчик:persil
            TeleGram:@persilj                                                                                                                          
"""
print(logo)
create_proxy_file()
def load_session():
    session_file = 'session.json'
    if os.path.exists(session_file):
        with open(session_file, 'r') as file:
            session = json.load(file)
        if 'api_id' in session and 'api_hash' in session:
            return session
    return None
def save_session(session):
    session_file = 'session.json'
    with open(session_file, 'w') as file:
        json.dump(session, file)

session = load_session()

if session is None:
    api_id = input('Введите API:')
    api_hash = input('Введите API-HASH:')
    session = {'api_id': api_id, 'api_hash': api_hash}
    save_session(session)
else:
    api_id = session['api_id']
    api_hash = session['api_hash']

def read_proxy_from_file(filename):
    try:
        with open(filename, 'r') as file:
            proxy = file.readline().strip()
        return proxy
    except FileNotFoundError:
        print("Файл с прокси не найден.")
        return None

def parse_proxy(proxy):
    pattern = r'^(.*?):(.*?)@(.*?):(.*?)$'
    match = re.match(pattern, proxy)
    if match:
        return {
            'proxy_type': 'socks5',
            'addr': match.group(3),
            'port': int(match.group(4)),
            'username': match.group(1),
            'password': match.group(2)
        }
    else:
        print("Некорректный формат прокси.")
        return None

use_proxy = input('Хотите использовать прокси? [да/нет]: ').lower()

device_model = 'SM0123456722'
app_version = '4.16.30-vx13'

if use_proxy == 'да':
    proxy = read_proxy_from_file('proxy.txt')
    if proxy:
        proxy_obj = parse_proxy(proxy)
        if proxy_obj:
            client = TelegramClient('session', api_id, api_hash, proxy=proxy_obj, device_model=device_model, app_version=app_version)
        else:
            client = TelegramClient('session', api_id, api_hash, device_model=device_model, app_version=app_version)
    else:
        client = TelegramClient('session', api_id, api_hash, device_model=device_model, app_version=app_version)
else:
    client = TelegramClient('session', api_id, api_hash, device_model=device_model, app_version=app_version)

try:
    client.start()
except SessionPasswordNeededError:
    password = input('Введите пароль 2FA:')
    client = client.start(password=password)
else:
    clear_console()
    print(logo)

account_name = client.get_me().first_name
print(f"Аккаунт: {account_name}")
delay = int(input('Введите значение таймера в секундах: '))         

def send_statistics(client, username, total_messages_sent, total_time, delay, rounds_completed):
    try:
        messages = client.get_messages(username, limit=1)
        for message in messages:
            if "**🤞Привествую:**" in message.text:
                # Удаляем его
                client.delete_messages(username, message.id)
        next_round_time = delay / 60
        total_seconds = int(total_time)
        message = (
            f"**🤞Привествую:**\n"
            f"**🚀Твоя статистика рассылки:**\n\n"
            f"**💬Отправлено сообщений:** `{total_messages_sent}`\n"
            f"**⏳Потрачено времени:** `{total_seconds}` **секунд**\n"
            f"**✔️Круг закончил ушел в сон на:** `{delay}` **секунд**\n"
            f"**🔄Кругов рассылки выполнено:** `{rounds_completed}`\n"
            f"**♻️Следующий Круг через:** `{next_round_time:.2f}` **минут**\n\n"
            f"**Загруженность ОЗУ:** `{psutil.virtual_memory().percent}`\n\n "
            f"**♾Продолжаю работать‼️**"
        )
        
        client.send_message(username, message, parse_mode='markdown')
        if psutil.virtual_memory().percent >= 96:
        
            client._entity_cache.clear()
            client._mb_entity_cache.hash_map.clear()
        
    except Exception as e:
        print(f"Ошибка при отправке статистики: {e}")
        logging.error(f"Error while sending statistics: {e}")


def send_start_message(client):
    try:
        client.send_message("@SpamBot", "/start")
        time.sleep(3)
        client.send_message("@SpamBot", "/start")
    except errors.FloodError as e:
        if e.message == "BAD_REQUEST":
            # При возникновении ошибки Flood: BAD_REQUEST, пытаемся отправить сообщение еще раз
            send_start_message(client)
        else:
            logging.error(f'Flood error: {e.message}')
    except Exception as exc:
        logging.error(f'Произошла непредвиденная ошибка: {exc}')

def create_groups_list(client, groups=None):
    if groups is None:
        groups = []

    for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.unread_count > 0:  
            groups.append(dialog) 

    return groups  

def spammer(client, send_stats, username,):
    total_messages_sent = 0
    start_time = datetime.now()
    rounds_completed = 1

    with client:
        for m in client.iter_messages('me', 1):
            msg = m

        while True:
            print("Рассылаю...")
            groups = create_groups_list(client) 
            for g in groups[:1000]:
                try:
                    client.forward_messages(g, msg, 'me')
                    total_messages_sent += 1
                except errors.ChatWriteForbiddenError as chat_write_error:
                    logging.error(f'Невозможно отправить сообщение в чат: {chat_write_error}') 
                    continue
                except errors.ForbiddenError as o:
                    logging.error(f'Не удалось отправить сообщение в чат: {o}')
                    client.delete_dialog(g)
                    if g.entity.username is not None:
                        logging.error(f'Ошибка: {o.message}. Аккаунт покинул @{g.entity.username}')
                    else:
                        logging.error(f'Ошибка: {o.message}. Аккаунт покинул {g.name}')
                        continue
                except errors.FloodError as e:
                    if e.seconds > 120:
                        continue
                    else:
                        logging.error(f'Flood: {e.message} Требуется ожидание {e.seconds} секунд')
                        sleep(e.seconds)
                        continue
                except errors.UserNotParticipantError as user_not_participant_error:
                    logging.error(f'UserNotParticipantError: {user_not_participant_error}')
                    continue
                except errors.MessageTooLongError:
                    logging.error(f'Message was too long ==> {g.name}')
                    continue
                except errors.BadRequestError as i:
                    logging.error(f'Flood: {i.message}')
                    if i.message == "BAD_REQUEST":
                        # При возникновении ошибки BAD_REQUEST отправляем сообщение боту
                        send_start_message(client)
                    continue
                except errors.RPCError as rpc_error:
                    logging.error(f'RPCError: {rpc_error}')
                    continue
                except InvalidBufferError:
                    logging.error('Ошибка при обработке буфера: InvalidBufferError')
                    continue
                except Exception as exc:
                    logging.error(f'Произошла непредвиденная ошибка: {exc}')
                    continue

            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            clear_console()
            account_name = client.get_me().first_name
            print_success(f"Аккаунт: {account_name}")
            print('Отправлено сообщений:', total_messages_sent)
            print(f"Ушел в сон на {delay} секунд...")

            if send_stats.lower() == "да":
                send_statistics(client, username, total_messages_sent, total_time, delay, rounds_completed)
            sleep(delay)
            rounds_completed += 1

            groups.clear()

def main():
    send_stats = input("Хотите отправлять статистику [Да/Нет]: ")
    if send_stats.lower() == "да":
        username = input("Введите юзернейм аккаунта: ")
    else:
        username = None

    spammer(client, send_stats, username)

if __name__ == '__main__':
    main() 