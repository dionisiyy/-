import json
import os
from datetime import datetime

def log_write(log_name, text):
    """Запись логов в файл с созданием директорий при необходимости"""
    os.makedirs(os.path.dirname(log_name), exist_ok=True)
    with open(log_name, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now()} - {text}\n")

def load_users_data():
    """Загрузка данных пользователей из JSON с созданием файла при отсутствии"""
    try:
        os.makedirs('data', exist_ok=True)
        if not os.path.exists('data/users.json'):
            with open('data/users.json', 'w', encoding='utf-8') as file:
                json.dump([], file)
            return []
        
        # Пробуем разные кодировки для чтения
        encodings = ['utf-8', 'utf-8-sig', 'cp1251']
        for encoding in encodings:
            try:
                with open('data/users.json', 'r', encoding=encoding) as file:
                    return json.load(file)
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Не удалось декодировать файл")
    except Exception as e:
        log_write("logs/errors.log", f"load_users_data: {str(e)}")
        return []

def save_users_data(data):
    """Сохранение данных пользователей в JSON"""
    try:
        with open('data/users.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        log_write("logs/errors.log", f"save_users_data: {str(e)}")
        return False

def write_users(chat_id, group, pgroup, dist_skip):
    """Запись/обновление данных пользователя с валидацией"""
    try:
        data = load_users_data()
        group = str(group).strip()
        pgroup = int(pgroup) if str(pgroup).isdigit() else 0
        dist_skip = str(dist_skip).strip()
        
        # Ищем пользователя
        user_index = next((i for i, u in enumerate(data) if u.get('chat_id') == chat_id), -1)
        
        user_data = {
            "chat_id": chat_id,
            "group": group,
            "pgroup": pgroup,
            "dist_skip": dist_skip
        }
        
        if user_index != -1:
            data[user_index] = user_data
            log_msg = f"updated: group={group}, pgroup={pgroup}, dist_skip={dist_skip}"
        else:
            data.append(user_data)
            log_msg = f"created: group={group}, pgroup={pgroup}, dist_skip={dist_skip}"
        
        if save_users_data(data):
            log_write('logs/user_changes.log', f"user: {chat_id} {log_msg}")
            return 0
        return -1
    except Exception as e:
        log_write("logs/errors.log", f"write_users: {str(e)}")
        return -1

def read_users(chat_id):
    """Чтение данных пользователя с значениями по умолчанию"""
    try:
        data = load_users_data()
        user = next((u for u in data if u.get('chat_id') == chat_id), None)
        
        if user:
            return [
                user['chat_id'],
                user.get('group', 'default_group'),
                user.get('pgroup', 0),
                user.get('dist_skip', '0')
            ]
        
        return [chat_id, "default_group", 0, "0"]
    except Exception as e:
        log_write("logs/errors.log", f"read_users: {str(e)}")
        return [chat_id, "default_group", 0, "0"]

def read_messages():
    """Чтение файла с сообщениями с обработкой ошибок"""
    default_messages = ["Сообщение не найдено"] * 8
    try:
        os.makedirs('src', exist_ok=True)
        encodings = ['utf-8', 'utf-8-sig', 'cp1251']
        
        for encoding in encodings:
            try:
                with open("src/messages.txt", "r", encoding=encoding) as file:
                    content = file.read().strip()
                    if content:
                        return content.split('////')
                    return default_messages
            except UnicodeDecodeError:
                continue
        
        return default_messages
    except Exception as e:
        log_write("logs/errors.log", f"read_messages: {str(e)}")
        return default_messages

def json_read(json_name):
    """Безопасное чтение JSON файла с обработкой кодировок"""
    if not os.path.exists(json_name):
        return None
        
    encodings = ['utf-8', 'utf-8-sig', 'cp1251']
    for encoding in encodings:
        try:
            with open(json_name, 'r', encoding=encoding) as file:
                return json.load(file)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    
    log_write("logs/errors.log", f"json_read: Не удалось прочитать файл {json_name}")
    return None