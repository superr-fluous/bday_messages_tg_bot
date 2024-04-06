from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from helpers.bot_types import NOTIFICATION_INFO_ROW
from db_manage.db_helpers import get_notification_row_by_id, get_notification_row_by_name, get_rows_from_ids
from helpers.helpers import groups_text_list, return_groups_list

display_notification_groups_stages = {
  'command': 'display_notification_groups',
  'step_1': 'notification_id_or_name',
}

async def start_display_notification_groups(update: Update, context: CallbackContext) -> str:
  """Начало диалога """
  await update.message.reply_text("Введи название или id поздравления (для отмены напиши /cancel)")

  return display_notification_groups_stages['step_1']

# обработка введеного id или названия группы
async def notification_id_name_handler(update: Update, context: CallbackContext) -> int | str:
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
    return display_notification_groups_stages['step_1']
  
  await update.message.reply_text('Поздравление найдено. Собираю информацию о группах...')

  groups_ids = return_groups_list(notification)

  if groups_ids is None:
    await update.message.reply_text("Не удалось получить группы для поздравления. Попробуй снова с другим значением или введи /cancel для отмены")
    return display_notification_groups_stages['step_1']
  
  if len(groups_ids):
    await update.message.reply_text("Поздравление не активно ни в каких группах")
    return ConversationHandler.END
  
  groups_configs = get_rows_from_ids(groups_ids, 'GROUPS')

  if groups_configs is None:
    await update.message.reply_text("Не удалось получить информацию о группах. Попробуй снова с другим значением или введи /cancel для отмены")
    return display_notification_groups_stages['step_1']
  
  if len(groups_ids) != len(groups_configs):
    await update.message.reply_text(f"Количество привязанных к поздравлению групп ({len(groups_ids)}) не совпадает с количеством полученных конфигов ({len(groups_configs)})")

  reply = groups_text_list(groups_configs, 'Поздравление активно в этих группах:')
  await update.message.reply_text(reply)

  return ConversationHandler.END
