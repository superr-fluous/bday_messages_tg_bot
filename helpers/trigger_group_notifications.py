from telegram.ext import CallbackContext

from typing import Literal

from db_helpers import get_group_row_by_id
from helpers.helpers import return_notifications_list
from telegram_api_helpers import start_notification_job, stop_notification_job

def trigger_group_notifications(context: CallbackContext, group_id: int, action: Literal['start'] | Literal['stop']) -> None:
  group_row = get_group_row_by_id(group_id)

  if group_row is not None:
      notifications = return_notifications_list(group_row)
      if notifications is not None:  
        for notification_id in notifications:
          start_notification_job(context, notification_id, group_id) if action == 'start' else stop_notification_job(context, notification_id, group_id)
