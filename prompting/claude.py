import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def prompt_claude(system_prompt, question, max_tokens=1000, model="claude-3-sonnet-20240229"):
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Error prompting Claude: {str(e)}")