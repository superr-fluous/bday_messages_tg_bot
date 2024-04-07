from telegram.ext import CallbackContext, ContextTypes
<<<<<<< HEAD
=======
from zoneinfo import ZoneInfo
>>>>>>> development

import logging
from datetime import datetime

from helpers.bot_types import NOTIFICATION_INFO, NOTIFICATION_INFO_ROW

### Отправка поздравдения в группу
async def send_message(context: CallbackContext) -> None:
  print('send message invoked')
  # try:
  job = context.job
  print(job)
  if job is not None and job.chat_id is not None and job.data is not None:
    print(f"Отправляю сообщение в {job.chat_id}")

    await context.bot.send_message(job.chat_id, text=job.data) # type: ignore[attr-defined]
    print(f"Сообщение отправлено в {job.chat_id}. Текст сообщения: {job.data}")
  else:
    print(f"Не удалось отправить сообщение в {job.chat_id}")

  # except Exception:
  #   print("Неизвестная ошибка во время отправки сообщения в {job.chat_id}")


### Регистрация задачи по отправке поздравления
def start_notification_job(context: CallbackContext, notification_info: NOTIFICATION_INFO_ROW, group_id: int) -> None:
  print(notification_info)
  id, name, date, groups, message = notification_info

  # try:
  print(f"Начинаю регистрацию отправки сообщения в {group_id}")
  date_object = datetime.fromisoformat(date).replace(tzinfo=ZoneInfo("Europe/Moscow"))
  job_name = f"{id}_{group_id}"
  
  if context.job_queue is not None:
    context.job_queue.run_once(send_message, date_object, data=message, chat_id=group_id, name=job_name) # type: ignore[attr-defined]
  # except Exception:
    #  print(f"Неизвестная ошибка во время регистрации отправки поздравления в {group_id}")

def stop_notification_job(context: ContextTypes.DEFAULT_TYPE, notification_id: int, group_id: int) -> None:
    # try:
    print(f"Удаляю задачу по отправке поздравления в {group_id}")

    if context.job_queue is not None:
      jobs = context.job_queue.get_jobs_by_name(f"{notification_id}_{group_id}") # type: ignore[attr-defined]

    if jobs:
      for job in jobs:
        job.schedule_removal()

    # except Exception:
      # print(f"Неизвестная ошибка во время удаления задачи для {group_id}")

def stop_all_group_notifications(context: CallbackContext, group_id: int) -> None:
  for job in context.job_queue.jobs():
    if job.name.split('_')[1] == str(group_id):
      job.schedule_remove()