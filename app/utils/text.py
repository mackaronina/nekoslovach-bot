import html

from aiogram.types import InputPollOption

from app.schemas import NewModel, PollModel, PollDict


def new_to_text(new: NewModel, new_tag: str) -> str:
    new_tag = new_tag.replace(' ', '_').replace('-', '_')
    return f'⚡️<b>{html.escape(new.title)}</b>\n\n{html.escape(new.text)}\n\n#{html.escape(new_tag)}'


def postprocess_comment(text: str) -> str:
    text = text.replace("'", '').replace('"', '').strip('. ')
    return html.escape(text[:1].upper() + text[1:])


def poll_model_to_dict(poll: PollModel) -> PollDict:
    return {
        'question': html.escape(poll.question),
        'options': [InputPollOption(text=html.escape(poll.options[0][:100])),
                    InputPollOption(text=html.escape(poll.options[1][:100]))],
        'is_anonymous': True,
    }
