from azure_model import generate_text


def build_prompt(prompt, textbook):
    original_text = textbook["full_chapter_text"]
    source_placeholders = ("{original_text}", "{textbook}", "{Textbook}", "[Article Text]")
    content = prompt.format(
        original_text=original_text,
        textbook=original_text,
        Textbook=original_text,
        topic=textbook["topic"],
    ).replace("[Article Text]", original_text)

    if not any(placeholder in prompt for placeholder in source_placeholders):
        content = f"{content}\n\nText:\n{original_text}"

    return content


def generate_summary(prompt, textbook):
    content = build_prompt(prompt, textbook)
    return generate_text(content, max_output_tokens=5000)