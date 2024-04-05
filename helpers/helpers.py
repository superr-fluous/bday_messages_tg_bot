from collections.abc import Iterator

from bot_types import GROUP_INFO_ROWS, NOTIFICATION_INFO_ROWS, GROUP_INFO_ROW, NOTIFICATION_INFO_ROW

DATE_DISPLAY_FORMAT = '%d.%m.%Y %H:%M:%S'

def return_id_from_str(id_or_title: str | None, configs: GROUP_INFO_ROWS | NOTIFICATION_INFO_ROWS) -> int | GROUP_INFO_ROW | NOTIFICATION_INFO_ROW | None:
  id: int | None = None
  info: NOTIFICATION_INFO_ROW | GROUP_INFO_ROW | None = None

  if id_or_title is None:
    return None

  if id_or_title.isnumeric():
    # group_id
    id = int(id_or_title)
  else:
    # group_name
    for config in configs:
      _, group_title_or_notification_name, *rest = config

      if id_or_title == group_title_or_notification_name:
        info = config
        break

  return id if info is None else info


def return_notifications_list(group_row: GROUP_INFO_ROW) -> Iterator[int] | None:
  notifications_str = group_row[3]

  if notifications_str is None:
    return None
  
  return map(lambda x: int(x), filter(lambda x: x != '', notifications_str.split(',')))

def return_groups_list(notification_row: NOTIFICATION_INFO_ROW) -> Iterator[int] | None:
  groups_str = notification_row[3]

  if groups_str is None:
    return None
  
  return map(lambda x: int(x), filter(lambda x: x != '', groups_str.split(',')))


def groups_text_list(rows: GROUP_INFO_ROWS, base_text = "Бот подключен в этих чатах:") -> str:
  text = base_text

  index = 1
  for info in rows:
    id, name, *rest = info
    text += f"\n{index}. Название: {name}, ID: {id}"
    index += 1
  
  return text

 
def notifications_text_list(rows: NOTIFICATION_INFO_ROWS, base_text = "Созданы эти поздравления:") -> str:
  text = base_text

  index = 1
  for info in rows:
    print(info)
    id, name, message = info[0], info[1], info[4]

    text += "\n*****"
    text += f"\n{index}. Название: {name}\n\tID поздравления: {id}"
    text += f"\n\tТекст сообщения: {message}"
    index += 1
  
  return text
