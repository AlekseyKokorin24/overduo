from aiogram.filters import BaseFilter
from main import ADMIN_IDS

class IsAdmin(BaseFilter):
    admin_ids = ADMIN_IDS

    def __init__(self, user_id: int) -> None:
        self.user_id - user_id

    def __call__(self) -> bool:
        return self.user_id in self.admin_ids
