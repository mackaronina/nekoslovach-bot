def escape_brackets(text: str) -> str:
    return text.replace('{', '{{').replace('}', '}}')
