from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from bot_types import GROUP_INFO_ROW
from db_helpers import get_group_row_by_id, get_group_row_by_name, get_rows_from_ids
from helpers.helpers import notifications_text_list, return_notifications_list

display_group_notifications_stages = {
  'command': 'display_group_notifications',
  'step_1': 'message',
}

async def start_display_group_notifications(update: Update, context: CallbackContext) -> str:
  """Начало диалога """
  await update.message.reply_text("Введи название или id группы (для отмены напиши /cancel)")

  return display_group_notifications_stages['step_1']

# обработка введеного id или названия группы
async def group_id_name_handler(update: Update, context: CallbackContext) -> int | str:
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
    return display_group_notifications_stages['step_1']
  
  await update.message.reply_text('Группа найдена. Собираю информацию о поздравлениях...')

  notifications_ids = return_notifications_list(group)

  if notifications_ids is None:
    await update.message.reply_text("Не удалось получить поздравления для группы. Попробуй снова с другим значением или введи /cancel для отмены")
    return display_group_notifications_stages['step_1']
  
  if len(notifications_ids):
    await update.message.reply_text("Для группы нет активных поздравлений")
    return ConversationHandler.END
  
  notifications_configs = get_rows_from_ids(notifications_ids, 'NOTIFICATIONS')

  if notifications_configs is None:
    await update.message.reply_text("Не удалось получить информацию о поздравлениях. Попробуй снова с другим значением или введи /cancel для отмены")
    return display_group_notifications_stages['step_1']
  
  if len(notifications_ids) != len(notifications_configs):
    await update.message.reply_text(f"Количество привязанных к группе поздравлений ({len(notifications_ids)}) не совпадает с количеством полученных конфигов ({len(notifications_configs)})")

  reply = notifications_text_list(notifications_configs, 'К группе привязаны эти поздравления:')
  await update.message.reply_text(reply)

  return ConversationHandler.END