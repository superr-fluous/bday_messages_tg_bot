from telegram import Update, Chat, ChatMemberUpdated, ChatMember
from telegram.ext import CallbackContext

from typing import Tuple, Optional

from db_helpers import remove_group_from_db, trigger_group_bot_status
from telegram_api_helpers import stop_all_group_notifications

def get_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)

    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)


    return was_member, is_member

async def handle_bot_chat_status(update: Update, context: CallbackContext) -> None:
  chat = update.effective_chat

  if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
    print('Bot status change in group')
    status_change = get_status_change(update.my_chat_member)

    if status_change is None:
       return
  
    left, joined = status_change
    print(f"Status: left - {left}, joined - {joined}")
    group_id, name = chat.id, chat.title

    if not left and joined:
       trigger_group_bot_status(group_id, name, 'online')
    
    if left and not joined:
       #? Наверное, стоит добавить третий вариант "removed"
       remove_group_from_db(group_id)
       stop_all_group_notifications(context, group_id)
    