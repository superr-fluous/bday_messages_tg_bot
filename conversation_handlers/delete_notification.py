from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from bot_types import NOTIFICATION_INFO_ROW
from db_helpers import delete_notification_from_table, get_notification_row_by_id, get_notification_row_by_name, remove_notification_from_group_db
from telegram_api_helpers import stop_notification_job

delete_notification_stages = {
  'command': 'delete_notification',
  'step_1': 'notification_id_name',
  'step_2': 'confirm',
}

async def start_delete_notification(update: Update, context: CallbackContext) -> int | str:
  """Начало диалога """
  await update.message.reply_text("Введи id или название поздравления (для отмены напиши /cancel)")

  return delete_notification_stages['step_1']


async def dn_notification_id_name(update: Update, context: CallbackContext) -> int | str:
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
    return delete_notification_stages['step_1']

  active_groups_number = len(list(filter(lambda x: x != '', notification[3].split(','))))

  context.chat_data['delete_notification_row'] = notification
  await update.message.reply_text(f"Поздравление активно в {active_groups_number} группах. Введи 'Да' для потверждения или /cancel для отмены")
  
  return delete_notification_stages['step_2']

async def dn_confirm(update: Update, context: CallbackContext) -> int:
  command = update.message.text

  if command.strip() == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  if command == 'Да':
    notification_row: NOTIFICATION_INFO_ROW | None = context.chat_data['delete_notification_row']

    if notification_row is None:
      await update.message.reply_text("Произошла ошибка во время обработки поздравления. Отмена действия")
      return ConversationHandler.END

    linked_groups = list(filter(lambda x: x != '', notification_row[3].split(',')))
    delete_notification_from_table(int(notification_row[0]))

    if len(linked_groups) != 0:
      for group_id in linked_groups:
        remove_notification_from_group_db(int(notification_row[0], linked_groups))
        stop_notification_job(context, int(notification_row[0]), int(group_id))
  
  await update.message.reply_text('Поздравление успешно удалено!')

  return ConversationHandler.END

