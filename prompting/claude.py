import anthropic
import os
from helpers_for_inference.prompt import get_system_prompt

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def prompt_claude(prompt_data, max_tokens=1000, model="claude-3-sonnet-20240229"):
    try:
        system_prompt = get_system_prompt(
            prompt_data['user']['organization_id'],
            prompt_data['url'],
            prompt_data['page_title'],
            prompt_data['selected_text'],
            prompt_data['active_element'],
            prompt_data['scroll_position']
        )
        system_prompt += f"User: {prompt_data['user']}"

        conversation_context = "\n\nPrevious conversation:\n"
        for msg in prompt_data['conversation_messages']:
            conversation_context += f"{msg['type'].capitalize()}: {msg['content']}\n"

        system_prompt += conversation_context

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt_data['question']}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Error prompting Claude: {str(e)}")