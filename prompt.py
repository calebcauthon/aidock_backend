from context_docs import get_relevant_context_docs

def get_system_prompt(url, page_title, selected_text, active_element, scroll_position):
    relevant_docs = get_relevant_context_docs(url)
    context_docs_text = "\n\n".join(relevant_docs) if relevant_docs else ""

    return f"""
URL: {url}
Page Title: {page_title}
Selected Text: {selected_text}
Active Element: {active_element}
Scroll Position: {scroll_position}

{context_docs_text}

The user is on the website {url}.

They're going to ask a question specifically about that URL. Use your knowledge of {page_title} to answer.
They want to know literally how to do something on the page. No conceptual answers. Explain using human actions like clicking.
Use HTML formatting to make your answer more readable. Do not include HTML elements **in** in the answer content.
For example, use list items to describe a list of things.

Be concise. Give only 1-2 sentences.
"""