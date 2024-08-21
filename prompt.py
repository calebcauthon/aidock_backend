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

<SiteSpecificContext>
{context_docs_text}
</SiteSpecificContext>

Be concise. Give only 1-2 sentence answers.
Dont make things up. Only answer based on the context provided.
"""