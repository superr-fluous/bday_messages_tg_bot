from dotenv import dotenv_values

from helpers.bot_types import GROUP_INFO, NOTIFICATION_INFO
from db_manage.db_helpers import add_group_to_notifications_db, add_notification_to_group_db, add_notification_to_table, delete_notification_from_table, get_all_groups_rows, get_all_notifications_rows, get_group_row_by_id, get_notification_row_by_id, remove_group_from_notifications_db, remove_notification_from_group_db, trigger_group_bot_status
from db_manage.db_purge import clear_db
from helpers.helpers import return_id_from_str

bot_config = dotenv_values(".env")
db_filename = bot_config.get('DB_FILENAME')

def test_add_group() -> True:
  # добавляем группу (т.к. в БД нет записей, то trigger_group_bot_status добавляет запись)
  trigger_group_bot_status(1, 'group1', 'online')

  # запрашиваем все группы
  all_rows = get_all_groups_rows()

  if len(all_rows) != 1:
    raise ValueError(f"test_add_group -> get_all_groups_rows: количество всех групп ({len(all_rows)}) не совпадает с количеством добавленных (1)")
  
  if all_rows[0][0] != 1:
    raise ValueError(f"test_add_group -> get_all_groups_rows: первый аргумент в строке ({all_rows[0][0]}) не равен записанному id (1)")

  lookup_row = get_group_row_by_id(1)

  if lookup_row is None:
    raise ValueError(f"test_add_group -> get_group_row_by_id: не найдена запись")

  return True

# вызывает test_add_group внутри
def test_bot_status_trigger() -> True:
  if test_add_group():
    # после вызова test_add_group в БД есть запись (1, 'group1', 'online', '')
    trigger_group_bot_status(1, 'group1', 'offline')
    lookup_row = get_group_row_by_id(1)

    if lookup_row is None:
      raise ValueError(f"test_bot_status_trigger: не найдена базовая запись")
    
    if lookup_row[2] != 'offline':
      raise ValueError(f"test_bot_status_trigger: expected OFFLINE got {lookup_row[2]}")
    
    trigger_group_bot_status(1, 'group1', 'online')
    lookup_row = get_group_row_by_id(1)

    if lookup_row is None:
      raise ValueError(f"test_bot_status_trigger: не найдена базовая запись")
    
    if lookup_row[2] != 'online':
      raise ValueError(f"test_bot_status_trigger: expected ONLINE got {lookup_row[2]}")
  
  return True


def test_notification_add_delete() -> True:
  notification_config: NOTIFICATION_INFO = {
    'id': 1,
    'date': 'date',
    'message': 'sup',
    'groups': 'sup'
  }

  add_notification_to_table(notification_config)

  lookup_notification = get_notification_row_by_id(notification_config.get('id'))

  if lookup_notification is None:
    raise ValueError("test_add_notification: не найдена запись")

  delete_notification_from_table(1)
  all_notifications = get_all_notifications_rows()

  if len(all_notifications) != 0:
    raise ValueError("test_add_notification: запись не была удалена")

  return True


def test_return_id_from_str() -> True:
  # бд пустая
  groups = get_all_groups_rows()
  notifications = get_all_notifications_rows()

  group_id = return_id_from_str(None, groups)
  notification_id = return_id_from_str(None, notifications)

  if group_id is not None:
    raise ValueError(f"test_return_id_from_str -> group_id: expected NONE got {group_id}")

  if notification_id is not None:
    raise ValueError(f"test_return_id_from_str -> notification_id: expected NONE got {notification_id}")

  group_id = return_id_from_str('1', groups)
  notification_id = return_id_from_str('1', notifications)

  if group_id != 1:
    raise ValueError(f"test_return_id_from_str -> group_id: expected 1 int got {group_id} {type(group_id)}")

  if notification_id != 1:
    raise ValueError(f"test_return_id_from_str -> group_id: expected 1 int got {notification_id} {type(notification_id)}")

  trigger_group_bot_status('1', 'group1', 'online')
  add_notification_to_table({ "id": 1, "message": 'sup', "date": "date", "groups": '', "name": 'sup'})

  all_groups = get_all_groups_rows()
  all_notifications = get_all_notifications_rows()

  group_id = return_id_from_str('group1', all_groups)
  notification_id = return_id_from_str('sup', all_notifications)

  if group_id is None or type(group_id) is int:
    raise ValueError(f"test_return_id_from_str -> name: expected group_info, got something else")
  
  if group_id is None or type(group_id) is int:
    raise ValueError(f"test_return_id_from_str -> notification_title: expected notification_info, got something else")
  
  if group_id[0] != 1:
    raise ValueError(f"test_return_id_from_str -> name: group id is not the expected one - got {group_id[0]}")
  
  if notification_id[0] != 1:
    raise ValueError(f"test_return_id_from_str -> notification_title: group id is not the expected one - got {notification_id[0]}")

  return True

def test_group_notification_links() -> True:
  notification_config: NOTIFICATION_INFO = { "id": 1, 'date': 'date', 'message': 'message', 'name': 'name', 'groups': ''}
  group_config: GROUP_INFO = { "id": 1, 'name': '' }

  add_notification_to_table(notification_config)
  trigger_group_bot_status(group_id=group_config.get('id'), name=group_config.get('name'), status='online')

  add_notification_to_group_db(notification_config.get('id'), group_config.get('id'))
  add_group_to_notifications_db(group_config.get('id'), notification_config.get('id'))

  lookup_notification = get_notification_row_by_id(notification_config.get('id'))
  lookup_group = get_group_row_by_id(group_config.get('id'))

  if lookup_notification is None:
    raise ValueError('test_group_notification_links: не добавлена запись')
  
  if lookup_notification[3] != '1':
    raise ValueError('test_group_notification_links: не cовпадение id')

  if lookup_group is None:
    raise ValueError('test_group_notification_links: не добавлена запись')
  
  if lookup_group[3] != '1':
    raise ValueError('test_group_notification_links: не cовпадение id')
  
  remove_notification_from_group_db(notification_config.get('id'), group_config.get('id'))
  remove_group_from_notifications_db(group_config.get('id'), notification_config.get('id'))

  lookup_notification = get_notification_row_by_id(notification_config.get('id'))
  lookup_group = get_group_row_by_id(group_config.get('id'))

  if lookup_notification is None:
    raise ValueError('test_group_notification_links: не добавлена запись')
  
  if lookup_notification[3] != '':
    raise ValueError('test_group_notification_links: не cовпадение id')

  if lookup_group is None:
    raise ValueError('test_group_notification_links: не добавлена запись')
  
  if lookup_group[3] != '':
    raise ValueError('test_group_notification_links: не cовпадение id')

def main() -> None:
  tests = [
    ("тест добавления групп", test_add_group),
    ('тест смены статуса бота в группе', test_bot_status_trigger),
    ('тест добавления/удаления уведомлений', test_notification_add_delete),
    ('тест получения id/конфига из id/названия группы/уведомления', test_return_id_from_str),
    ('тест добавления/удаления уведомлений/групп из списка соотв. групп/уведомлений', test_group_notification_links)
  ]

  total_tests = len(tests)
  passed_tests = 0

  for index, test in enumerate(tests):
    print(f"Тест#{index + 1}: {test_message}")
    clear_db()
    test_message, callback_fn = test
    callback_fn()
    passed_tests += 1
  
  print(f"Успешно пройдены {passed_tests} из {total_tests}")
  

if __name__ == "__main__":
    main()