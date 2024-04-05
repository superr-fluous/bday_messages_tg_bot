import sqlite3
from dotenv import dotenv_values

bot_config = dotenv_values(".env")

def main() -> None:
  db_filename = bot_config.get('DB_FILENAME')

  if db_filename is None:
     raise ValueError("Не указан файл БД в .env")
  
  connection = sqlite3.connect(db_filename)
  cursor = connection.cursor()

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS GROUPS (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  bot_status TEXT NOT NULL,    
  notifications TEXT NOT NULL    
  )''')

  cursor.execute("CREATE UNIQUE INDEX group_id ON GROUPS(id)")

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS NOTIFICATIONS (
  id INTEGER PRIMARY KEY,
  name TEXT,
  date TEXT NOT NULL,
  groups TEXT NOT NULL,
  message TEXT NOT NULL 
  )
  ''')

  cursor.execute("CREATE UNIQUE INDEX notification_id ON NOTIFICATIONS(id)")

  connection.commit()
  connection.close()

if __name__ == "__main__":
    main()