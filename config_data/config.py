import os
import dotenv

from dataclasses import dataclass

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    PRIMARY_KEYS: set[str]
 
@dataclass
class Config:
    tg_bot: TgBot

def load_config() -> Config:
    dotenv.load_dotenv()
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN_OVERDUE'),
            admin_ids=list(map(int, os.getenv('ADMIN_IDS').split())),
            PRIMARY_KEYS=set()
        )
    )

