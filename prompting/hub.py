from prompting.claude import prompt_claude
from prompting.chatgpt import prompt_chatgpt
def execute_prompt(service, prompt_data):
    if service == 'claude':
        return prompt_claude(prompt_data)
    elif service == 'chatgpt':
        return prompt_chatgpt(prompt_data)
    else:
        raise ValueError(f"Unknown prompting service: {service}")