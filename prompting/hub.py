from prompting.claude import prompt_claude

def execute_prompt(service, prompt_data):
    if service == 'claude':
        return prompt_claude(prompt_data)
    else:
        raise ValueError(f"Unknown prompting service: {service}")