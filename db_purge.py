import sqlite3
from dotenv import dotenv_values

bot_config = dotenv_values(".env")
db_filename = bot_config.get('DB_FILENAME')


def clear_db() -> None:
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  cursor.execute('DELETE FROM GROUPS')
  cursor.execute('DELETE FROM NOTIFICATIONS')

  connection.commit()
  connection.close()

def main() -> None:
  clear_db()

if __name__ == 'main':
  main()