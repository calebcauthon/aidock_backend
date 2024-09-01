from context_docs import get_relevant_context_docs

def get_system_prompt(url, page_title, selected_text, active_element, scroll_position):
    relevant_docs = get_relevant_context_docs(url)
    context_docs_text = "\n\n".join([f"Document Name: {doc['document_name']}\nDocument Text: {doc['document_text']}" for doc in relevant_docs]) if relevant_docs else ""

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


So give answers confidently. Dont say "Based on the context provided" or anything like that.
Start your answer with 'Sure, I can help with that', and restate the purpose of the chat.
Continue with 1-2 short sentences of the answer.
"""