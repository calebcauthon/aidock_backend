from openai import OpenAI
from typing import List, Dict
from flask import current_app
import os

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def prompt_chatgpt(prompt_data, model: str = "gpt-4o") -> str:
    messages: List[Dict[str, str]] = []

    # Add system message
    system_prompt = f"User: {prompt_data['user']}\n"
    system_prompt += f"URL: {prompt_data['url']}\n"
    system_prompt += f"Page Title: {prompt_data['page_title']}\n"
    system_prompt += f"Selected Text: {prompt_data['selected_text']}\n"
    system_prompt += f"Active Element: {prompt_data['active_element']}\n"
    system_prompt += f"Scroll Position: {prompt_data['scroll_position']}\n"
    messages.append({"role": "system", "content": system_prompt})

    # Add previous conversation messages
    for msg in prompt_data['conversation_messages']:
        messages.append({"role": msg['type'], "content": msg['content']})

    # Add the current user question
    messages.append({"role": "user", "content": prompt_data['question']})
    try:

        response = client.chat.completions.create(model=model,
        messages=messages)

        return response.choices[0].message.content.strip()
    except Exception as e:
        current_app.logger.error(f"Error in prompt_chatgpt: {str(e)}")
        raise
