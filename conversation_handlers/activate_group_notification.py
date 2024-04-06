from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import time

from helpers.bot_types import GROUP_INFO_ROW, NOTIFICATION_INFO_ROW
from db_manage.db_helpers import add_group_to_notifications_db, add_notification_to_group_db, get_group_row_by_id, get_group_row_by_name, get_notification_row_by_id, get_notification_row_by_name, get_rows_from_ids
from helpers.helpers import return_notifications_list
from helpers.telegram_api_helpers import start_notification_job

activate_group_notification = {
  'command': 'activate_group_notification',
  'step_1': 'notification_id_name',
  'step_2': 'group_id_name',
}

async def start_activate_group_notification(update: Update, context: CallbackContext) -> str:
  """Начало диалога """
  await update.message.reply_text("Введи id или название поздравления (для отмены напиши /cancel)")

  return activate_group_notification['step_1']

# обработка введеного текста поздравления
# префикс agn (activate group notification, чтобы с другими хэндлерами не путать)
async def agn_notification_id_name_handler(update: Update, context: CallbackContext) -> int | str:
  id_or_name = update.message.text
  stripped = id_or_name.strip()
  notification: NOTIFICATION_INFO_ROW | None

  if stripped == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  if stripped.isnumeric():
    notification = get_notification_row_by_id(int(stripped))
  else:
    notification = get_notification_row_by_name(stripped)

  
  if notification is None:
    await update.message.reply_text("Не удалось найти указанное поздравление. Попробуй снова с другим значением или введи /cancel для отмены")
    return activate_group_notification['step_1']
  
  context.chat_data['activate_notification_row'] = notification

  await update.message.reply_text('Поздравление найдено. Введи id или название группы')

  return activate_group_notification['step_2']

# обработка введеного id или названия группы
async def agn_group_id_name_handler(update: Update, context: CallbackContext) -> int | str:
  id_or_name = update.message.text
  stripped = id_or_name.strip()
  group: GROUP_INFO_ROW | None

  if stripped == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  if stripped.isnumeric():
    group = get_group_row_by_id(int(stripped))
  else:
    group = get_group_row_by_name(stripped)

  
  if group is None:
    await update.message.reply_text("Не удалось найти указанную группу. Попробуй снова с другим значением или введи /cancel для отмены")
    return activate_group_notification['step_2']
  
  group_active_notifications = return_notifications_list(group)

  if group_active_notifications is None:
    await update.message.reply_text("Вероятно, произошла ошибка при включении поздравлений в этой группе. Добавление уведомлений невозможно. Попробуй снова с другим значением или введи /cancel для отмены")
  
  notification_row: None | NOTIFICATION_INFO_ROW = context.chat_data['activate_notification_row']
  notification_id = notification_row[0]

  if notification_id is None:
    await update.message.reply_text("Ошибка. Не удалось обработать id поздравления. Отмена действия")
    return ConversationHandler.END
  
  if notification_id in group_active_notifications:
    await update.message.reply_text("Поздравление уже активно в группе.  Попробуй снова с другим значением или введи /cancel для отмены")

    # TODO? можно добавить опцию проверки job для поздравления в группе

    return activate_group_notification['step_2']
  
  start_notification_job(context, notification_row, group[0])
  add_notification_to_group_db(notification_id, group[0])
  add_group_to_notifications_db(group[0], notification_id)

  reply_notification = notification_row[0] if notification_row[1] == '' else notification_row[1]
  await update.message.reply_text(f"Поздравление '{reply_notification}' активированого в группе '{group[1]}'")

  return ConversationHandler.END
