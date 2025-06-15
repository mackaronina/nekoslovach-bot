from typing import List

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TG_ANONYMOUS_ID = 777000


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore",
                                      case_sensitive=False)


class BotSettings(ConfigBase):
    token: SecretStr = Field(alias='BOT_TOKEN')
    webhook_domain: SecretStr
    host: str = '0.0.0.0'
    port: int = 80
    report_chat_id: int
    channel_chat_id: int
    comments_chat_id: int
    timestamp: int = 0


class OpenaiSettings(ConfigBase):
    token: SecretStr = Field(alias='OPENAI_TOKEN')
    url: str = Field(alias='OPENAI_URL')
    temperature: float = 1
    model_name: str


class TagsSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='tags_')
    default: str = 'предложка'
    all: List[str] = [
        'спорт', 'финансы', 'технологии', 'международные отношения', 'политика', 'общество', 'наука',
        'красота и здоровье', 'шоу-бизнес', 'компьютерные игры', 'погода', 'мнения', 'астрология', 'туризм',
        'военные действия', 'культура', 'фильмы и сериалы', 'интервью', 'историческая правда', 'проишествия',
        'власть', 'образование', 'криминал', 'разоблачение', 'благотворительность', 'мода', 'ИТ-технологии',
        'кибербезопасность', 'изменение климата', 'медицина', 'выборы', 'коррупция', 'развлечения',
        'социальные сети', 'мистика', 'кулинария', 'история успеха', 'литература и книги',
        'развенчивание мифов', 'архитектура и урбанистика', 'беженцы и мигранты', 'аниме', 'терроризм',
        'археология', 'страшная история', 'природа', 'забавная история', 'криптовалюта', 'лайфхаки',
        'инсайдерская информация'
    ]


class Settings(BaseSettings):
    bot: BotSettings = Field(default_factory=BotSettings)
    openai: OpenaiSettings = Field(default_factory=OpenaiSettings)
    tags: TagsSettings = Field(default_factory=TagsSettings)


settings = Settings()
