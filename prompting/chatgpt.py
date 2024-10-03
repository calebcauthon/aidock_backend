from openai import OpenAI
from typing import List, Dict
from flask import current_app
import os
from helpers_for_inference.prompt import get_system_prompt

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def prompt_chatgpt(prompt_data, model: str = "gpt-4o") -> str:
    messages: List[Dict[str, str]] = []


    system_prompts = get_system_prompt(
        prompt_data['user']['organization_id'],
        prompt_data['url'],
        prompt_data['page_title'],
        prompt_data['selected_text'],
        prompt_data['active_element'],
        prompt_data['scroll_position']
    )

    for system_prompt in system_prompts:
      if system_prompt['type'] == 'text':
          messages.append({"role": "system", "content": system_prompt['content']})
      elif system_prompt['type'] == 'image':
          messages.append({
              "role": "user",
              "content": [
                  {"type": "text", "text": f"Image Name: {system_prompt['image_name']}"},
                  {
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{system_prompt['image_base64']}"
                      }
                  }
              ]
          })

    # Add previous conversation messages
    for msg in prompt_data['conversation_messages']:
        role = msg['type'] if msg['type'] in ['system', 'user'] else 'user'
        messages.append({"role": role, "content": msg['content']})

    # Add the current user question
    messages.append({"role": "user", "content": prompt_data['question']})
    try:

        response = client.chat.completions.create(model=model,
        messages=messages)

        return response.choices[0].message.content.strip()
    except Exception as e:
        current_app.logger.error(f"Error in prompt_chatgpt: {str(e)}")
        raise
