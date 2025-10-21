import logging
import pandas as pd
import csv
import os
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8449976484:AAEH_IPxs2JyPoPTyd2Gf3DOf8uPjnt-mCw"

# Состояния для ConversationHandler
(
    NAME, PROJECT_NAME, PROJECT_DESCRIPTION, PATENT,
    PHONE, EMAIL, SOCIAL_MEDIA, TEAM_MEMBERS,
    CITY, UNIVERSITY, FACULTY
) = range(11)

# Состояния для зрителя
VIEWER_NAME, VIEWER_PHONE = range(2)

# Текст о конкурсе
COMPETITION_INFO = """
«Донская сборка» - крупнейший на Юге России ежегодный конкурс изобретателей, технологических предпринимателей и инноваторов ⚙️

Конкурс-смотр изобретений проходит на базе ДГТУ — опорного вуза Ростовской области при поддержке Правительства региона в Промышленном коворкинге «Garaж». Ежегодно Донская сборка отвечает на современные инновационные вызовы общества соответствующими номинациями. 
Каждый участник может представить свой проект перед экспертами, получить обратную связь по улучшению и применению изобретения, установить новые деловые контакты и в случае победы получить поддержку на развитие проекта.
"""


# Клавиатура с кнопками
def get_main_keyboard():
    keyboard = [
        ["ℹ️ Информация о конкурсе"],
        ["📝 Подать заявку", "🏆 Номинации"],
        ["👀 Хочу быть зрителем!", "📅 Программа мероприятия"],
        ["📞 Контакты"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот конкурса-смотра «Донская сборка» - крупнейшего события для изобретателей на Юге России!

Выбери нужный раздел:"""

    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())


# Обработчик кнопки "Информация о конкурсе"
async def competition_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(COMPETITION_INFO)


# Обработчик кнопки "Номинации"
async def nominations(update: Update, context: CallbackContext) -> None:
    nominations_text = """
🏆 Номинации конкурса «Донская сборка 2025»:

• «Изобретение года»
• «Студенческая разработка» 
• «Агротехнология года»
• «Юный изобретатель»
• «Цифровые технологии»
• «Биоинженерия»
• «Акселерационная» 
• «Робототехника» (новинка 2025 года!)

+ специальные номинации 🤫

Конкурс пройдет в смешанном формате (онлайн и оффлайн) регистрация на мероприятие продлится до 26 ноября — успей подать заявку! 🔥
"""
    await update.message.reply_text(nominations_text)


# Обработчик кнопки "Программа мероприятия"
async def event_program(update: Update, context: CallbackContext) -> None:
    program_text = "📅 Программа мероприятия еще на стадии доработки, но совсем скоро она появится здесь!"
    await update.message.reply_text(program_text)


# Обработчик кнопки "Контакты"
async def contacts(update: Update, context: CallbackContext) -> None:
    contacts_text = """
📞 Контакты:

Подробную информацию можно получить по телефону 8 (863) 238-17-22 или по электронной почте garazh@donstu.ru — Промышленный коворкинг «Garaж».
"""
    await update.message.reply_text(contacts_text)


# Начало процесса подачи заявки
async def start_application(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "📝 Отлично! Ты начинаешь подачу заявки на конкурс «Донская сборка»!\n\n"
        "Для начала, напиши своё ФИО (подающий заявку автоматически записывается как спикер):",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


# Получение ФИО
async def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name

    await update.message.reply_text(
        f"👤 Приятно познакомиться, {user_name}!\n\n"
        "Теперь напиши название твоей разработки:"
    )
    return PROJECT_NAME


# Получение названия разработки
async def get_project_name(update: Update, context: CallbackContext) -> int:
    project_name = update.message.text
    context.user_data['project_name'] = project_name

    await update.message.reply_text(
        f"💡 Название разработки: {project_name}\n\n"
        "Теперь опиши подробно свой проект (основная идея, назначение, особенности):"
    )
    return PROJECT_DESCRIPTION


# Получение описания проекта
async def get_project_description(update: Update, context: CallbackContext) -> int:
    project_description = update.message.text
    context.user_data['project_description'] = project_description

    await update.message.reply_text(
        "📋 Есть ли у тебя патент на эту разработку?\n\n"
        "Напиши 'Да' или 'Нет', а если есть - укажи номер патента:"
    )
    return PATENT


# Получение информации о патенте
async def get_patent(update: Update, context: CallbackContext) -> int:
    patent_info = update.message.text
    context.user_data['patent'] = patent_info

    await update.message.reply_text(
        "📞 Теперь укажи свой контактный телефон:"
    )
    return PHONE


# Получение телефона
async def get_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    context.user_data['phone'] = phone

    await update.message.reply_text(
        "📧 Укажи свою электронную почту (необязательно):",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True)
    )
    return EMAIL


# Получение email
async def get_email(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Пропустить":
        email = "Не указано"
    else:
        email = update.message.text
    context.user_data['email'] = email

    await update.message.reply_text(
        "🔗 Укажи ссылку на Telegram или ВКонтакте (необязательно):",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True)
    )
    return SOCIAL_MEDIA


# Получение соцсетей
async def get_social_media(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Пропустить":
        social_media = "Не указано"
    else:
        social_media = update.message.text
    context.user_data['social_media'] = social_media

    await update.message.reply_text(
        "👥 Укажи ФИО участников команды (если работаешь один - напиши 'нет'):",
        reply_markup=ReplyKeyboardRemove()
    )
    return TEAM_MEMBERS


# Получение информации о команде
async def get_team_members(update: Update, context: CallbackContext) -> int:
    team_members = update.message.text
    context.user_data['team_members'] = team_members

    await update.message.reply_text(
        "🏙️ Укажи свой город:"
    )
    return CITY


# Получение города
async def get_city(update: Update, context: CallbackContext) -> int:
    city = update.message.text
    context.user_data['city'] = city

    await update.message.reply_text(
        "🎓 Укажи своё учебное заведение - ВУЗ (если ты студент):",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True)
    )
    return UNIVERSITY


# Получение ВУЗа
async def get_university(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Пропустить":
        university = "Не указано"
    else:
        university = update.message.text
    context.user_data['university'] = university

    await update.message.reply_text(
        "📚 Укажи свой факультет (если ты студент):",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True)
    )
    return FACULTY


# Получение факультета и завершение заявки
async def get_faculty(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Пропустить":
        faculty = "Не указано"
    else:
        faculty = update.message.text
    context.user_data['faculty'] = faculty

    # Сохраняем заявку
    success = await save_application(update, context)

    if success:
        # Показываем сводку
        summary_text = f"""
✅ ЗАЯВКА ПОДАНА УСПЕШНО!

📋 Твои данные:
• 👤 ФИО (спикер): {context.user_data['name']}
• 💡 Название разработки: {context.user_data['project_name']}
• 📝 Описание: {context.user_data['project_description']}
• 📄 Патент: {context.user_data['patent']}
• 📞 Телефон: {context.user_data['phone']}
• 📧 Email: {context.user_data['email']}
• 🔗 Соцсети: {context.user_data['social_media']}
• 👥 Команда: {context.user_data['team_members']}
• 🏙️ Город: {context.user_data['city']}
• 🎓 ВУЗ: {context.user_data['university']}
• 📚 Факультет: {context.user_data['faculty']}

📞 С тобой свяжутся организаторы для уточнения деталей участия.

🏆 Удачи в конкурсе!
        """
    else:
        summary_text = """
❌ Произошла ошибка при сохранении заявки.

Но не волнуйся! Твои данные сохранены, и мы обязательно с тобой свяжемся.

Попробуй подать заявку позже или свяжись с организаторами напрямую.
        """

    await update.message.reply_text(
        summary_text,
        reply_markup=get_main_keyboard()
    )

    # Очищаем данные
    context.user_data.clear()

    return ConversationHandler.END


# Начало регистрации зрителя
async def start_viewer_registration(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "👀 Отлично! Чтобы присутствовать на мероприятии в качестве зрителя, укажи своё ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return VIEWER_NAME


# Получение ФИО зрителя
async def get_viewer_name(update: Update, context: CallbackContext) -> int:
    viewer_name = update.message.text
    context.user_data['viewer_name'] = viewer_name

    await update.message.reply_text(
        f"👤 Приятно познакомиться, {viewer_name}!\n\n"
        "Теперь укажи свой контактный телефон:"
    )
    return VIEWER_PHONE


# Получение телефона зрителя и завершение регистрации
async def get_viewer_phone(update: Update, context: CallbackContext) -> int:
    viewer_phone = update.message.text
    context.user_data['viewer_phone'] = viewer_phone

    # Сохраняем заявку зрителя
    success = await save_viewer_application(update, context)

    if success:
        summary_text = f"""
✅ РЕГИСТРАЦИЯ ЗРИТЕЛЯ ПРОШЛА УСПЕШНО!

📋 Твои данные:
• 👤 ФИО: {context.user_data['viewer_name']}
• 📞 Телефон: {context.user_data['viewer_phone']}

Мы свяжемся с тобой перед мероприятием для подтверждения регистрации!

✨ Ждем тебя на «Донской сборке 2025»!
        """
    else:
        summary_text = """
❌ Произошла ошибка при сохранении регистрации.

Попробуй зарегистрироваться позже или свяжись с организаторами напрямую.
        """

    await update.message.reply_text(
        summary_text,
        reply_markup=get_main_keyboard()
    )

    # Очищаем данные
    context.user_data.clear()

    return ConversationHandler.END


# Сохранение заявки в Excel и CSV
async def save_application(update: Update, context: CallbackContext) -> bool:
    try:
        # Данные заявки
        application_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'УЧАСТНИК',
            'user_id': update.effective_user.id,
            'username': update.effective_user.username or 'Нет username',
            'name': context.user_data['name'],
            'project_name': context.user_data['project_name'],
            'project_description': context.user_data['project_description'],
            'patent': context.user_data['patent'],
            'phone': context.user_data['phone'],
            'email': context.user_data['email'],
            'social_media': context.user_data['social_media'],
            'team_members': context.user_data['team_members'],
            'city': context.user_data['city'],
            'university': context.user_data['university'],
            'faculty': context.user_data['faculty']
        }

        # Сохраняем в CSV (основной способ)
        csv_success = save_to_csv(application_data)

        # Сохраняем в Excel (дополнительный способ)
        excel_success = save_to_excel(application_data)

        if csv_success or excel_success:
            logger.info(f"✅ Заявка участника сохранена: {application_data['name']} - {application_data['project_name']}")
            return True
        else:
            logger.error("❌ Не удалось сохранить заявку ни в одном формате")
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении заявки: {e}")
        return False


# Сохранение заявки зрителя
async def save_viewer_application(update: Update, context: CallbackContext) -> bool:
    try:
        # Данные зрителя
        viewer_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'ЗРИТЕЛЬ',
            'user_id': update.effective_user.id,
            'username': update.effective_user.username or 'Нет username',
            'name': context.user_data['viewer_name'],
            'phone': context.user_data['viewer_phone']
        }

        # Сохраняем в CSV (основной способ)
        csv_success = save_to_csv(viewer_data)

        # Сохраняем в Excel (дополнительный способ)
        excel_success = save_to_excel(viewer_data)

        if csv_success or excel_success:
            logger.info(f"✅ Заявка зрителя сохранена: {viewer_data['name']}")
            return True
        else:
            logger.error("❌ Не удалось сохранить заявку зрителя ни в одном формате")
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении заявки зрителя: {e}")
        return False


# Сохранение в CSV
def save_to_csv(application_data):
    try:
        file_exists = os.path.exists('applications.csv')

        with open('applications.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=application_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(application_data)

        logger.info("✅ Данные сохранены в CSV")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении в CSV: {e}")

        # Пытаемся сохранить в backup CSV
        try:
            backup_filename = f"backup_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(backup_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=application_data.keys())
                writer.writeheader()
                writer.writerow(application_data)
            logger.info(f"✅ Создан backup CSV: {backup_filename}")
            return True
        except Exception as backup_error:
            logger.error(f"❌ Ошибка создания backup CSV: {backup_error}")
            return False


# Сохранение в Excel
def save_to_excel(application_data):
    try:
        # Создаём DataFrame из новых данных
        new_df = pd.DataFrame([application_data])

        # Пытаемся сохранить с обработкой ошибок
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Проверяем существование файла
                if os.path.exists('applications.xlsx'):
                    existing_df = pd.read_excel('applications.xlsx')
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    updated_df = new_df

                # Сохраняем файл
                updated_df.to_excel('applications.xlsx', index=False)
                logger.info("✅ Данные сохранены в Excel")
                return True

            except PermissionError:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Excel файл заблокирован, повторная попытка {attempt + 2}...")
                    # Ждём немного перед повторной попыткой
                    import time
                    time.sleep(1)
                else:
                    logger.warning("⚠️ Не удалось сохранить в Excel (файл заблокирован), но CSV сохранён")
                    return False  # Не критично, если CSV сохранился

            except Exception as e:
                logger.error(f"❌ Ошибка при сохранении в Excel: {e}")
                return False

    except Exception as e:
        logger.error(f"❌ Критическая ошибка при работе с Excel: {e}")
        return False


# Отмена заявки
async def cancel_application(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "❌ Подача заявки отменена.",
        reply_markup=get_main_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END


# Отмена регистрации зрителя
async def cancel_viewer_registration(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "❌ Регистрация зрителя отменена.",
        reply_markup=get_main_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "ℹ️ Информация о конкурсе":
        await competition_info(update, context)
    elif text == "🏆 Номинации":
        await nominations(update, context)
    elif text == "📞 Контакты":
        await contacts(update, context)
    elif text == "📝 Подать заявку":
        await start_application(update, context)
    elif text == "👀 Хочу быть зрителем!":
        await start_viewer_registration(update, context)
    elif text == "📅 Программа мероприятия":
        await event_program(update, context)
    else:
        await update.message.reply_text(
            "Используй кнопки для навигации! 📱",
            reply_markup=get_main_keyboard()
        )


# Основная функция
def main() -> None:
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Настройка ConversationHandler для заявки участника
    participant_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 Подать заявку$"), start_application)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project_name)],
            PROJECT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project_description)],
            PATENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_patent)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            SOCIAL_MEDIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_media)],
            TEAM_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_team_members)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_university)],
            FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_faculty)],
        },
        fallbacks=[CommandHandler("cancel", cancel_application)]
    )

    # Настройка ConversationHandler для регистрации зрителя
    viewer_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^👀 Хочу быть зрителем!$"), start_viewer_registration)],
        states={
            VIEWER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_viewer_name)],
            VIEWER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_viewer_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel_viewer_registration)]
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(participant_conv_handler)
    application.add_handler(viewer_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("🚀 Бот запущен! Остановите сочетанием Ctrl+C")
    print("📊 Заявки сохраняются в applications.csv и applications.xlsx")
    print("📝 Логи сохраняются в bot.log")
    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")