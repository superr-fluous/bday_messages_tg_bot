from typing import TypedDict, Literal, Tuple, List

TYPE_BOT_STATUS_STARTED = Literal['started']
TYPE_BOT_STATUS_STOPPED = Literal['stopped']

GROUP_INFO = TypedDict('GROUP_INFO', {
    "name": str,
    "bot_status": TYPE_BOT_STATUS_STARTED | TYPE_BOT_STATUS_STOPPED,
    "notifications": List[int],
    "id": int,
})

NOTIFICATION_INFO = TypedDict('NOTIFICATION_INFO', {
    "message": str,
    "date": str,
    "groups": List[int],
    "name": str | None,
    "id": int,
})

GROUP_INFO_ROW = Tuple[int, str, str, str] # id, name, bot_status, notifications
NOTIFICATION_INFO_ROW = Tuple[int, str, str, str, str] # id, name, date, groups, messages

GROUP_INFO_ROWS = List[GROUP_INFO_ROW]
NOTIFICATION_INFO_ROWS = List[NOTIFICATION_INFO_ROW]