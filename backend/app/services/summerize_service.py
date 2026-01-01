from google import genai
import json

client = genai.Client()  # API key should be set as env variable

def summarize_text_and_category(text: str) -> dict:
    prompt_text = f"""
Read the following text and do two things:
1. Summarize it in a short, clear paragraph in simple English.
2. Detect its category freely.

Text:
{text}

Return JSON like this:
{{"summary": "...", "category": "..."}}
"""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt_text
    )

    output_text = response.text.strip()

    # Remove triple backticks if present
    if output_text.startswith("```"):
        output_text = output_text.split("\n", 1)[1]
        output_text = output_text.rsplit("```", 1)[0]

    # Parse JSON
    try:
        parsed = json.loads(output_text)
        summary = parsed.get("summary", "").strip()
        category = parsed.get("category", "").strip()
    except:
        summary = output_text
        category = output_text

    return {"summary": summary, "category": category}
