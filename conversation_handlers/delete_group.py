from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from helpers.bot_types import GROUP_INFO_ROW, NOTIFICATION_INFO_ROW
from db_manage.db_helpers import get_group_row_by_id, get_group_row_by_name, remove_group_from_db
from helpers.telegram_api_helpers import stop_all_group_notifications

delete_group_stages = {
  'command': 'delete_group',
  'step_1': 'group_id_name',
  'step_2': 'confirm',
}

async def start_delete_group(update: Update, context: CallbackContext) -> int | str:
  """Начало диалога """
  await update.message.reply_text("Введи id или название группы (для отмены напиши /cancel)")

  return delete_group_stages['step_1']


async def dg_group_id_name(update: Update, context: CallbackContext) -> int | str:
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
    return delete_group_stages['step_1']

  active_notifications_number = len(list(filter(lambda x: x != '', group[3].split(','))))

  context.chat_data['delete_group_row'] = group
  await update.message.reply_text(f"В группе активно {active_notifications_number} поздравлений. Введи 'Да' для потверждения или /cancel для отмены")
  
  return delete_group_stages['step_2']

async def dg_confirm(update: Update, context: CallbackContext) -> int:
  command = update.message.text

  if command.strip() == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  if command == 'Да':
    group_row: NOTIFICATION_INFO_ROW | None = context.chat_data['delete_group_row']

    if group_row is None:
      await update.message.reply_text("Произошла ошибка во время обработки группы. Отмена действия")
      return ConversationHandler.END

    remove_group_from_db(group_row[0])
    stop_all_group_notifications(context, group_row[0])

  
  await update.message.reply_text('Поздравление успешно удалено!')

  return ConversationHandler.END

