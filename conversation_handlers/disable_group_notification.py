from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from helpers.bot_types import GROUP_INFO_ROW, NOTIFICATION_INFO_ROW
from db_manage.db_helpers import get_group_row_by_id, get_group_row_by_name, get_notification_row_by_id, get_notification_row_by_name, remove_group_from_notifications_db, remove_notification_from_group_db
from helpers.telegram_api_helpers import stop_notification_job

disable_group_notification = {
  'command': 'disable_group_notification',
  'step_1': 'group_id_name',
  'step_2': 'notification_id_name',
}

async def start_disable_group_notification(update: Update, context: CallbackContext) -> str:
  """Начало диалога """
  await update.message.reply_text("Введи id или название группы (для отмены напиши /cancel)")

  return disable_group_notification['step_1']

# обработка введеного текста поздравления
# префикс dgn (disable group notification, чтобы с другими хэндлерами не путать)
async def dgn_group_id_name_handler(update: Update, context: CallbackContext) -> int | str:
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
    await update.message.reply_text("Не удалось найти указаннаю группу. Попробуй снова с другим значением или введи /cancel для отмены")
    return disable_group_notification['step_1']
  
  context.chat_data['dgn_group_row'] = group

  await update.message.reply_text('Группа найдена. Введи id или название поздравления')

  return disable_group_notification['step_2']

# обработка введеного id или названия группы
async def dgn_notification_id_name_handler(update: Update, context: CallbackContext) -> int | str:
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
    return disable_group_notification['step_1']
  
  group_row = context.chat_data['dgn_group_row']

  stop_notification_job(context, notification[0], group_row[0])
  remove_notification_from_group_db(notification[0], group_row[0])
  remove_group_from_notifications_db(group_row[0], notification[0])

  reply_notification = notification[0] if notification[1] == '' else notification[1]
  await update.message.reply_text(f"Поздравление '{reply_notification}' удалено из группы '{group_row[1]}'")

  return ConversationHandler.END
