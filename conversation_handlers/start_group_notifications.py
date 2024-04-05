from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from bot_types import GROUP_INFO_ROW
from db_helpers import get_group_row_by_id, get_group_row_by_name
from helpers.trigger_group_notifications import trigger_group_notifications

start_group_notifications_stages = {
  'command': 'start_group',
  'step_1': 'group_id_name',
}

async def start_start_group_notification(update: Update, context: CallbackContext) -> int:
  """Начало диалога """
  await update.message.reply_text("Введи id или название группы (для отмены напиши /cancel)")

  return start_group_notifications_stages['step_1']

async def sgn_group_id_name(update: Update, context: CallbackContext) -> int | str:
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
    return start_group_notifications_stages['step_1']

  trigger_group_notifications(context, int(group[0]), 'start')

  await update.message.reply_text("Уведомления запущены!")

  return ConversationHandler.END
