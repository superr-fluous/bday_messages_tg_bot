import sqlite3

from bot_types import GROUP_INFO_ROWS, GROUP_INFO_ROW, NOTIFICATION_INFO_ROW, NOTIFICATION_INFO_ROWS, NOTIFICATION_INFO, GROUP_INFO
from dotenv import dotenv_values

from typing import List, Literal
from collections.abc import Iterator

bot_config = dotenv_values(".env")
db_filename = bot_config.get("DB_FILENAME")

def get_group_row_by_id(group_id: int) -> GROUP_INFO_ROW:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  row = cursor.execute(f"SELECT * FROM GROUPS WHERE id=?", (group_id,)).fetchone()
  connection.commit()
  connection.close()

  return row

def get_group_row_by_name(group_name: str) -> GROUP_INFO_ROW:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  row = cursor.execute(f"SELECT * FROM GROUPS WHERE name=?", (group_name,)).fetchone()
  connection.commit()
  connection.close()

  return row


def get_notification_row_by_id(notification_id: int) -> NOTIFICATION_INFO_ROW:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  row = cursor.execute(f"SELECT * FROM NOTIFICATIONS WHERE id=?", (notification_id,)).fetchone()
  connection.commit()
  connection.close()

  return row

def get_notification_row_by_name(notification_name: str) -> NOTIFICATION_INFO_ROW:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  row = cursor.execute(f"SELECT * FROM NOTIFICATIONS WHERE name=?", (notification_name,)).fetchone()
  connection.commit()
  connection.close()

  return row


def get_all_groups_rows() -> GROUP_INFO_ROWS:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  rows = cursor.execute(f"SELECT * FROM GROUPS").fetchall()
  connection.commit()
  connection.close()

  return rows


def get_all_notifications_rows() -> GROUP_INFO_ROWS:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  rows = cursor.execute(f"SELECT * FROM NOTIFICATIONS").fetchall()
  connection.commit()
  connection.close()

  return rows
  

def get_rows_from_ids(ids: list[int] | Iterator[int], table: Literal['NOTIFICATIONS'] | Literal['GROUPS']) -> GROUP_INFO_ROWS | NOTIFICATION_INFO_ROWS:
  query = f"SELECT * FROM {table} WHERE"
  base_condition = "id="

  for index, id in enumerate(ids):
    query += f" {base_condition}{id}"

    if index != len(ids) - 1:
      query += " OR"
  
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  rows = cursor.execute(query).fetchall()
  connection.commit()
  connection.close()

  return rows

def add_notification_to_table(config: NOTIFICATION_INFO) -> None:
  notification_row: NOTIFICATION_INFO_ROW = (config.get('id'), config.get('name'), config.get('date'), config.get('groups'), config.get('message'))

  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  cursor.execute("INSERT INTO NOTIFICATIONS VALUES(?, ?, ?, ?, ?)", notification_row)

  connection.commit()
  connection.close()

def delete_notification_from_table(notification_id: int) -> List[int]:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  cursor.execute(f"DELETE FROM NOTIFICATIONS WHERE id={notification_id}")

  connection.commit()
  connection.close()

def add_notification_to_group_db(notification_id: int, group_id: int) -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();
  group_notifications: str = cursor.execute("SELECT notifications FROM GROUPS WHERE id=?", (group_id,)).fetchone()[0]
  new_group_notifications = ','.join(list(filter(lambda x: x != '', group_notifications.split(','))) + [str(notification_id)])

  cursor.execute('UPDATE GROUPS SET notifications=? WHERE id=?', (new_group_notifications, group_id))
  connection.commit()
  connection.close()

def remove_notification_from_group_db(notification_id: int, group_id: int) -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  group_notifications: str = cursor.execute("SELECT notifications FROM GROUPS WHERE id=?", (str(group_id))).fetchone()[0]
  new_group_notifications = ','.join(filter(lambda x: x != '', group_notifications.split(',')) - [str(notification_id)])

  cursor.execute('UPDATE GROUPS SET notifications=? WHERE id=?', (new_group_notifications, group_id))
  connection.commit()
  connection.close()

def add_group_to_notifications_db(group_id: int, notification_id: int) -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  notification_groups: str = cursor.execute("SELECT groups FROM NOTIFICATIONS WHERE id=?", (notification_id,)).fetchone()[0]
  new_notification_groups = ','.join(list(filter(lambda x: x != '', notification_groups.split(','))) + [str(group_id)])

  cursor.execute('UPDATE NOTIFICATIONS SET groups=? WHERE id=?', (new_notification_groups, notification_id))
  connection.commit()
  connection.close()

def remove_group_from_notifications_db(group_id: int, notification_id: int) -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  notification_groups: str = cursor.execute("SELECT groups FROM NOTIFICATIONS WHERE id=?", (notification_id,)).fetchone()[0]
  new_notification_groups = ','.join(list(filter(lambda x: x != '', notification_groups.split(','))) - [str(group_id)])

  cursor.execute('UPDATE GROUPS SET notifications=? WHERE id=?', (new_notification_groups, group_id))
  connection.commit()
  connection.close()

def trigger_group_bot_status(group_id: str, name: str, status: Literal['online'] | Literal['offline']) -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();
  cursor.execute(f"INSERT INTO GROUPS VALUES({group_id}, '{name}', 'online', '') ON CONFLICT(id) DO UPDATE SET bot_status='{status}'")

  connection.commit()
  connection.close()

def remove_group_from_db(group_id: int) -> None:

  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor();

  group_notifications: str = cursor.execute('SELECT notifications from GROUPS where id=?', (group_id,)).fetchone()[0]
  notification_ids: List[str] = list(filter(lambda x: x != '', group_notifications.split(',')))
  
  if len(notification_ids) > 0:
    for notification_id in notification_ids:
      notification_groups = cursor.execute('SELECT groups from NOTIFICATIONS where id=?', (int(notification_id),)).fetchone()
      new_notification_groups = list(notification_groups.split(',')) - [str(group_id)]
      cursor.execute('UPDATE NOTIFICATIONS SET groups=? WHERE id=?', (','.join(new_notification_groups), group_id))

  print(f'DELETING GROUP {group_id}')
  cursor.execute('DELETE FROM GROUPS WHERE id=?', (group_id,))

  connection.commit()
  connection.close()