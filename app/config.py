from pathlib import Path

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Don't change it
TG_ANONYMOUS_ID = 777000
BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8', extra='ignore',
                                      case_sensitive=False)


class OpenaiSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='OPENAI_')
    TOKEN: SecretStr
    URL: str = 'https://api.groq.com/openai/v1'
    TEMPERATURE: float = 1.2
    MODEL_NAME: str = 'meta-llama/llama-4-maverick-17b-128e-instruct'


class TagsSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='TAGS_')
    DEFAULT: str = 'предложка'
    ALL: list[str] = [
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


class Settings(ConfigBase):
    BOT_TOKEN: SecretStr
    WEBHOOK_DOMAIN: str
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    REPORT_CHAT_ID: int
    CHANNEL_CHAT_ID: int
    COMMENTS_CHAT_ID: int
    TIME_ZONE: str = 'UTC'
    USE_POLLING: bool = False
    AUTO_POSTING: bool = True
    POST_INTERVAL_HOURS: int = 12
    OPENAI: OpenaiSettings = Field(default_factory=OpenaiSettings)
    TAGS: TagsSettings = Field(default_factory=TagsSettings)


SETTINGS = Settings()
