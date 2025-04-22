import datetime
import src.tranzactions as tr
import sys
from datetime import timedelta

sys.path.insert(1, '../')
from api.parcer import parcer

month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
             'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
days_list = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 
             'Пятница', 'Суббота', 'Воскресенье']

def format_time_delta(delta):
    """Форматирование временного интервала в часы и минуты"""
    total_seconds = abs(int(delta.total_seconds()))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return hours, minutes

def validate_lesson_item(item):
    """Проверка структуры элемента расписания"""
    required_keys = ['number', 'time-start', 'time-end', 'subject', 'teacher', 'room']
    return all(key in item for key in required_keys)

def par_output(chat_id):
    """Основная функция для получения информации о парах"""
    try:
        getter = parcer()
        messages = tr.read_messages()
        today = datetime.datetime.now()
        
        user_info = tr.read_users(chat_id)
        if len(user_info) < 4:
            return str(messages[0])
            
        group, pgroup, dist_skip = user_info[1], str(user_info[2]), str(user_info[3])
        
        for days_ahead in range(5):
            current_date = today + timedelta(days=days_ahead)
            date_str = f"{days_list[current_date.weekday()]}, {current_date.day} {month_list[current_date.month - 1]}"
            
            if getter.get_info(group, current_date) != 0:
                continue
                
            data = tr.json_read(f'cache/{group}.json')
            if not data or not isinstance(data, list):
                continue
                
            for item in data:
                if not validate_lesson_item(item):
                    continue
                    
                # Пропускаем дистанционные пары если нужно
                if dist_skip == '1' and item.get('room') == "дист":
                    continue
                    
                # Проверяем подгруппу
                subject = item.get('subject', '')
                if len(subject) >= 5:
                    subject_pg = subject[-5]
                    if subject_pg in ('1', '2') and subject_pg != pgroup:
                        continue
                
                try:
                    # Парсим время начала и конца пары
                    start_time = datetime.datetime.strptime(item['time-start'], '%H:%M').time()
                    end_time = datetime.datetime.strptime(item['time-end'], '%H:%M').time()
                    
                    lesson_start = current_date.replace(hour=start_time.hour, minute=start_time.minute)
                    lesson_end = current_date.replace(hour=end_time.hour, minute=end_time.minute)
                    now = datetime.datetime.now()
                    
                    # Проверяем три случая:
                    # 1. Пара идет прямо сейчас
                    if lesson_start <= now <= lesson_end:
                        delta = now - lesson_start
                        hours, minutes = format_time_delta(delta)
                        return messages[10] % (
                            hours, minutes, date_str, item['number'],
                            item['subject'], item['time-start'],
                            item['time-end'], item['teacher'], item['room']
                        )
                    
                    # 2. Пара начнется в ближайшие 30 минут
                    elif lesson_start - timedelta(minutes=30) <= now < lesson_start:
                        delta = lesson_start - now
                        hours, minutes = format_time_delta(delta)
                        return messages[9] % (
                            hours, minutes, date_str, item['number'],
                            item['subject'], item['time-start'],
                            item['time-end'], item['teacher'], item['room']
                        )
                    
                    # 3. Пара будет в другой день
                    elif days_ahead > 0 and now < lesson_start:
                        return messages[8] % (
                            days_ahead, date_str, item['number'],
                            item['subject'], item['time-start'],
                            item['time-end'], item['teacher'], item['room']
                        )
                        
                except (ValueError, KeyError) as e:
                    tr.log_write('logs/errors.log', f"core.py/time_parse: {str(e)}")
                    continue
                    
        return str(messages[1])  # Если пар нет в ближайшие 5 дней

    except Exception as e:
        tr.log_write('logs/errors.log', f"core.py/para_output: {str(e)}")
        return "Произошла ошибка при получении расписания. Попробуйте позже."