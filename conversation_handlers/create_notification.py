from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import time

from bot_types import NOTIFICATION_INFO
from db_helpers import add_notification_to_table

create_notification_stages = {
  'command': 'create_notification',
  'step_1': 'message',
  'step_2': 'date',
  'step_3': 'name',
}

async def start_create_notification(update: Update, context: CallbackContext) -> str:
  """Начало диалога """
  await update.message.reply_text("Введи текст поздравления (для отмены напиши /cancel)")

  return create_notification_stages['step_1']

# обработка введеного текста поздравления
async def notification_message_handler(update: Update, context: CallbackContext) -> int | str:
  message = update.message.text

  if message.strip() == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  context.chat_data['create_notification_message'] = message

  await update.message.reply_text("Введи дату отправки поздравления (пример '2024-01-31 00:00') ")

  return create_notification_stages['step_2']

async def notification_date_handler(update: Update, context: CallbackContext) -> int | str:
  date = update.message.text

  if date.strip() == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END
  # TODO проверка даты
  context.chat_data['create_notification_date'] = date

  await update.message.reply_text("Введи название поздравления, чтобы его было проще найти (/skip чтобы пропустить)")

  return create_notification_stages['step_3']

async def notification_name_handler(update: Update, context: CallbackContext) -> int | str:
  name = update.message.text
  
  if name.strip() == '/cancel':
    await update.message.reply_text('Отмена действия')
    return ConversationHandler.END

  notification_config: NOTIFICATION_INFO = {
    'message': context.chat_data['create_notification_message'],
    'date': context.chat_data['create_notification_date'],
    'name': '' if name == '/skip' else name, # если не нашли /skip, то имя
    'groups': '',
    'id': int(time.time()),
  }

  # try:
  add_notification_to_table(notification_config)
  feedback_name = f"название - {notification_config['name']}, " if notification_config['name'] != '' else ''
  feedback_id = f"id - {notification_config['id']}"
  await update.message.reply_text(f"Поздравление успешно создано! ({feedback_name}{feedback_id})")
  # except Exception as err:
    # print(err)
    # await update.message.reply_text('Произошла ошибка во время создания поздравления. Отмена действия')
    
  return ConversationHandler.END

