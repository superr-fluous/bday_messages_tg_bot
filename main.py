from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ChatMemberHandler,
    CallbackContext
)

from dotenv import dotenv_values
from typing import Final

from conversation_handlers.activate_group_notification import agn_group_id_name_handler, agn_notification_id_name_handler, start_activate_group_notification, activate_group_notification
from conversation_handlers.create_notification import notification_date_handler, notification_message_handler, notification_name_handler, start_create_notification, create_notification_stages
from conversation_handlers.delete_group import start_delete_group, dg_group_id_name, dg_confirm, delete_group_stages
from conversation_handlers.delete_notification import dn_confirm, dn_notification_id_name, start_delete_notification, delete_notification_stages
from conversation_handlers.disable_group_notification import dgn_group_id_name_handler, dgn_notification_id_name_handler, start_disable_group_notification, disable_group_notification
from conversation_handlers.dispay_group_notifications import group_id_name_handler, start_display_group_notifications, display_group_notifications_stages
from conversation_handlers.display_notification_groups import notification_id_name_handler, start_display_notification_groups, display_notification_groups_stages
from conversation_handlers.start_group_notifications import sgn_group_id_name, start_start_group_notification, start_group_notifications_stages
from conversation_handlers.stop_group_notifications import spgn_group_id_name, stop_group_notifications_stages
from helpers.helpers import groups_text_list, notifications_text_list
from db_helpers import get_all_groups_rows, get_all_notifications_rows
from other_handlers.bot_chat_status import handle_bot_chat_status

HELP_RESPONSE: Final[str] = '''
Чтобы использовать бота надо добавить его в группу и написать /start c тэгом бота (/stop - для остановки).
После этого ботом можно управлять через личные сообщения. Есть следующие команды:
    1. /display_all_groups - список всех групп, в которых был прописан /start
    2. /display_all_notifications - список всех созданных поздравлений
    3. /display_group_notifications - список всех уведомлений, привязанных к конкретной группе
    4. /display_notification_groups - список всех групп, где привязано конкретное поздравение
    5. /create_notification - создать поздравение
    6. /activate_group_notification - привязать поздравение к группе (после привязки поздравение будет активно)
    7. /disable_group_notification - отвязать поздравение от группы (уведомлени не будет послано в группе)
    8. /delete_notification - удалить поздравение
    9. /start_group - запустить бота в группе (после добавления бот по умолчанию запущен)
    10. /stop_group - бот не будет слать уведомления, пока не будет снова запущен
'''

bot_config = dotenv_values(".env")

FILTER_ADMIN_PRIVATE = filters.ChatType.PRIVATE & (~ filters.User(bot_config.get('ADMIN_USERNAME'))) # type: ignore[attr-defined]

# Архитектура
### 1. Хардкодится админ, все сообщения не от админа игнорируются
### 2. Админ может управлять ботом через личные сообщения
### 3. Админ может через ЛС добавлять новые оповещения, удалять существующие, включать / отключать оповещение в беседах

# Прочее
# Обработчики команд пользователя
async def help_admin(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(HELP_RESPONSE)


async def display_all_groups(update: Update, context: CallbackContext) -> None:
    all_groups = get_all_groups_rows()
    reply_text = groups_text_list(all_groups, "Бот подключен в этих чатах:")

    await update.message.reply_text(reply_text)


async def display_all_notifications(update: Update, context: CallbackContext) -> None:
    all_notifications = get_all_notifications_rows()
    reply_text = notifications_text_list(all_notifications)
    
    await update.message.reply_text(reply_text)


def main() -> None:
    """Запуск бота"""
    # Подключаем бота телеграм через токен
    # try:
    print("Бот запускается...")
    application = Application.builder().token(bot_config.get('TOKEN')).build()

    '''
    2. Добавить обработку mention бота в группе
    4. Сделать логгирование в файл. В целом можно сделать нормальное логирование с параметрами, чтобы потом экспортировать логи
    5. Перенести на MongoDB
    6. Мне не нравится структура проекта и файлов (надо бы причесать)
    7. Получить бы какой-то базовый конфиг бота
    '''

    application.add_handler(ChatMemberHandler(handle_bot_chat_status)) 

    ### команды для ЛС
    # help
    application.add_handler(CommandHandler('help', help_admin, FILTER_ADMIN_PRIVATE))

    ## отображение групп, поздравлений без фильтрации
    application.add_handler(CommandHandler('display_all_groups', display_all_groups, FILTER_ADMIN_PRIVATE))
    application.add_handler(CommandHandler('display_all_notifications', display_all_notifications, FILTER_ADMIN_PRIVATE))

    ## отображение групп, поздравлений с фильтрацией по группе или поздравлению
    # все поздравления в группе
    group_notifications_conversation = ConversationHandler(
        entry_points=[CommandHandler(display_group_notifications_stages['command'], start_display_group_notifications, FILTER_ADMIN_PRIVATE)],
        states={
            display_group_notifications_stages['step_1']: [MessageHandler(None, group_id_name_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(group_notifications_conversation)

    # все группы у поздравления
    notification_groups_conversation = ConversationHandler(
        entry_points=[CommandHandler(display_notification_groups_stages['command'], start_display_notification_groups, FILTER_ADMIN_PRIVATE)],
        states={
            display_notification_groups_stages['step_1']: [MessageHandler(None, notification_id_name_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(notification_groups_conversation)

    ## управление поздравлениями
    # создание поздравления
    create_notification_conversation = ConversationHandler(
        entry_points=[(CommandHandler(create_notification_stages['command'], start_create_notification, FILTER_ADMIN_PRIVATE))],
        states={
            create_notification_stages['step_1']: [MessageHandler(None, notification_message_handler)],
            create_notification_stages['step_2']: [MessageHandler(None, notification_date_handler)],
            create_notification_stages['step_3']: [MessageHandler(None, notification_name_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(create_notification_conversation)

    # включение поздравления для группы
    add_notification_to_group_conversation = ConversationHandler(
        entry_points=[CommandHandler(activate_group_notification['command'], start_activate_group_notification, FILTER_ADMIN_PRIVATE)],
        states={
            activate_group_notification['step_1']: [MessageHandler(None, agn_notification_id_name_handler)],
            activate_group_notification['step_2']: [MessageHandler(None, agn_group_id_name_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(add_notification_to_group_conversation)

    # выключение поздравления для группы
    remove_notification_from_group_conversation = ConversationHandler(
        entry_points=[CommandHandler(disable_group_notification['command'], start_disable_group_notification, FILTER_ADMIN_PRIVATE)],
        states={
            disable_group_notification['step_1']: [MessageHandler(None, dgn_group_id_name_handler)],
            disable_group_notification['step_2']: [MessageHandler(None, dgn_notification_id_name_handler)],
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(remove_notification_from_group_conversation)

    # удаление поздравления из БД
    delete_notification_conversation = ConversationHandler(
        entry_points=[CommandHandler(delete_notification_stages['command'], start_delete_notification, FILTER_ADMIN_PRIVATE)],
        states={
            delete_notification_stages['step_1']: [MessageHandler(None, dn_notification_id_name)],
            delete_notification_stages['step_2']: [MessageHandler(None, dn_confirm)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(delete_notification_conversation)

    # удаление группы из БД
    delete_group_conversation = ConversationHandler(
        entry_points=[CommandHandler(delete_group_stages['command'], start_delete_group, FILTER_ADMIN_PRIVATE)],
        states={
            delete_group_stages['step_1']: [MessageHandler(None, dg_group_id_name)],
            delete_group_stages['step_2']: [MessageHandler(None, dg_confirm)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(delete_group_conversation)

    ## управление состоянием бота в группе
    # включение всех уведомлений в группе
    start_group_notifications_conversation = ConversationHandler(
        entry_points=[CommandHandler(start_group_notifications_stages['command'], start_start_group_notification, FILTER_ADMIN_PRIVATE)],
        states={
            start_group_notifications_stages['step_1']: [MessageHandler(None, sgn_group_id_name)],
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(start_group_notifications_conversation)

    # отключение всех уведомлений в группе
    stop_group_notifications = ConversationHandler(
        entry_points=[CommandHandler(stop_group_notifications_stages['command'], start_start_group_notification, FILTER_ADMIN_PRIVATE)],
        states={
            stop_group_notifications_stages['step_1']: [MessageHandler(None, spgn_group_id_name)]
        },
        fallbacks=[CommandHandler('cancel', lambda: ConversationHandler.END)]
    )
    application.add_handler(stop_group_notifications)

    async def message_base(update: Update, context: CallbackContext):
        print(f'Message from {update.effective_chat} containing {update.effective_message}')

    application.add_handler(MessageHandler(None, message_base))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    # except Exception as err:
    #     print("Ошибка во время запуска бота")
    #     print(f"Ошибка: {err}")

if __name__ == "__main__":
    main()