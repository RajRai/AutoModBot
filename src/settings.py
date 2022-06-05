from dataclasses import dataclass


@dataclass
class AutomodSettings:
    prune_message_threshold: int


@dataclass
class Settings:
    automod: AutomodSettings


settings = Settings(AutomodSettings(1))
settings.automod.prune_message_threshold = 1
