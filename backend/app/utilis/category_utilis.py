import re

def split_ai_categories(ai_text: str) -> list[str]:
    if not ai_text:
        return []

    parts = re.split(r",|/|&|\band\b", ai_text.lower())

    # set ko remove kar diya, order preserve rahe
    result = []
    for part in parts:
        clean = part.strip().title()
        if clean and clean not in result:
            result.append(clean)

    return result