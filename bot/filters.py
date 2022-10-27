import re
from typing import Optional, Union

from pymongo.collection import Collection
from telegram import Message
from telegram.ext import MessageFilter
from telegram.ext.filters import DataDict

from config import get_debug
from db.mongo import get_db


class TrustedDB:
    def __init__(self, db_name: str):
        self._coll: Collection = get_db(db_name).users

    def is_trusted(self, user_id: str) -> bool:
        return self._coll.find_one({"_id": user_id}) is not None


_trusted_db = TrustedDB("trusted")


class TrustedFilter(MessageFilter):
    name = "Filter.trusted"

    def filter(self, message: Message) -> Optional[Union[bool, DataDict]]:
        if get_debug():
            return True
        return _trusted_db.is_trusted(message.from_user.id)


class AdminFilter(MessageFilter):
    name = "Filters.admin"

    def filter(self, message) -> bool:
        if get_debug():
            return True
        return message.from_user.id in {
            a.user.id for a in message.chat.get_administrators()
        }



class OnlyAdminOnOthersFilter(MessageFilter):
    name = "Filters.onlyAdminOnOthers"

    def filter(self, message: Message) -> bool:
        if get_debug():
            return True
        if message.reply_to_message is not None:
            return message.from_user.id in {
                a.user.id for a in message.chat.get_administrators()
            }

        return True


admin_filter = AdminFilter()
only_admin_on_others = OnlyAdminOnOthersFilter()
trusted_filter = TrustedFilter()
