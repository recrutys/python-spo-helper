import hashlib
import base64
import requests
from services.db import *

def sha256_b64(text):
    """Хеширует текст в SHA256 и кодирует в base64 для пароля"""
    text_bytes = text.encode('utf-8')
    sha256_hash = hashlib.sha256(text_bytes).digest()
    base64_encoded = base64.b64encode(sha256_hash).decode('utf-8')

    return base64_encoded

def auth(login, password):
    # Авторизация в системе
    try:
        hashed_password = sha256_b64(password)

        # Делаем запрос на API авторизации
        response = requests.post(
            'https://spo.rso23.ru/services/security/login',
            json={
                'login': login,
                'password': hashed_password,
                'isRemember': True
            },
            timeout=10
        )

        # Если ответ успешный, то..
        if response.status_code == 200:
            # Получаем ответ сайта
            data = response.json()

            # извлечение информации о студенте
            tenant_key = list(data.get('tenants', {}).keys())[0] if data.get('tenants') else None
            tenant = data.get('tenants', {}).get(tenant_key, {})
            student_role = tenant.get('studentRole', {})
            students = student_role.get('students', [])

            # Проверяем есть ли студенты
            if not students:
                return {
                    'success': False,
                    'error': 'Студент не найден в ответе API'
                }

            student = students[0]

            student_info = {
                'student_id': student.get('id'),
                'first_name': student.get('firstName', ''),
                'last_name': student.get('lastName', ''),
                'group_name': student.get('groupName', '')
            }

            full_name = f"{student_info['last_name']} {student_info['first_name']}".strip()

            return {
                'success': True,
                'session': response.cookies,
                'student_id': student_info['student_id'],
                'full_name': full_name,
                'group_name': student_info['group_name']
            }
        else:
            return {
                'success': False,
                'error': f'Ошибка API: {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка соединения: {str(e)}'
        }

def refresh_session(tg_user_id):
    """Обновляет сессию пользователя"""
    try:
        db = load_db()
        if tg_user_id not in db:
            return {'success': False, 'error': 'Пользователь не найден'}

        user_data = db[tg_user_id]
        login = user_data['login']
        password = user_data['password']

        # Повторная авторизация
        auth_result = auth(login, password)

        if auth_result['success']:
            # Обновляем сессию в базе
            user_data['session'] = auth_result['session'].get_dict() if 'session' in auth_result else None
            save_db(db)
            return {'success': True, 'session': auth_result['session']}
        else:
            return {'success': False, 'error': auth_result['error']}

    except Exception as e:
        return {'success': False, 'error': f'Ошибка обновления сессии: {str(e)}'}

def get_user(tg_user_id):
    """Получает пользователя из локальной базы по Telegram ID"""
    try:
        db = load_db()

        if tg_user_id in db:
            user_data = db[tg_user_id]
            return {
                'success': True,
                'user': user_data
            }
        else:
            return {
                'success': False,
                'error': 'Пользователь не найден в базе'
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка загрузки базы: {str(e)}'
        }

def get_grades(session_cookies, student_id, tg_user_id=None):
    """Получение и форматирование оценок с автоматическим обновлением сессии"""
    try:
        response = requests.get(
            f'https://spo.rso23.ru/services/reports/current/performance/{student_id}',
            cookies=session_cookies,
            timeout=10
        )

        # Если сессия устарела
        if response.status_code == 401 and tg_user_id:
            # Пытаемся обновить сессию
            refresh_result = refresh_session(tg_user_id)
            if refresh_result['success']:
                # Получаем обновленные данные пользователя
                user_result = get_user(tg_user_id)
                if user_result['success']:
                    new_session = user_result['user']['session']
                    # Повторяем запрос с новой сессией
                    response = requests.get(
                        f'https://spo.rso23.ru/services/reports/current/performance/{student_id}',
                        cookies=new_session,
                        timeout=10
                    )

        if response.status_code == 200:
            grades_data = response.json()
            formatted_grades = _format_grades_simple(grades_data)
            return {'success': True, 'data': formatted_grades}
        else:
            return {'success': False, 'error': 'Не удалось получить оценки'}

    except Exception as e:
        return {'success': False, 'error': f'Ошибка получения оценок: {str(e)}'}

def _format_grades_simple(grades_data):
    """Форматирование оценок"""

    if not grades_data.get('daysWithMarksForSubject'):
        return "📊 Оценок пока нет"

    text = ""

    # Перевод оценок
    mark_translate = {'Five': '5', 'Four': '4', 'Three': '3', 'Two': '2', 'One': '1'}

    # Типы пропусков
    absence_types = {
        'IsAbsentByValidReason': '🟡 УП',
        'IsAbsentByNotValidReason': '🔴 НП',
        'SickLeave': '🏥 Б'
    }

    # Статистика
    total_days = 0
    present_days = 0

    # Проходим по предметам
    for subject in grades_data['daysWithMarksForSubject']:
        subject_name = subject.get('subjectName', 'Предмет')
        average = subject.get('averageMark', 'нет')
        days = subject.get('daysWithMarks', [])

        text += f"<b>{subject_name}</b>\n"

        # Собираем все оценки в одну строку
        all_marks = []
        for day in days:
            total_days += 1

            date = day.get('day', '')[:10]  # 2025-09-30
            formatted_date = f"{date[8:10]}.{date[5:7]}"  # 30.09

            marks = day.get('markValues', [])
            absence = day.get('absenceType')

            if absence:
                # Пропуск
                all_marks.append(f"{formatted_date}({absence_types.get(absence, '?')})")
            elif marks:
                # Оценки
                present_days += 1
                marks_str = '/'.join([mark_translate.get(m, m) for m in marks])
                all_marks.append(f"{formatted_date}({marks_str})")

        # Объединяем все оценки через запятую в моноширинном шрифте
        if all_marks:
            text += f"<code>Оценки: {', '.join(all_marks)}</code>\n"
        else:
            text += "<code>Оценки: нет</code>\n"

        text += f"Средний балл: <b>{average}</b>\n\n"

    # Добавляем посещаемость
    if total_days > 0:
        attendance = (present_days / total_days) * 100
        text += f"<i>Посещаемость: {attendance:.1f}% ({present_days}/{total_days} дней)</i>"

    return text