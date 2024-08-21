def get_system_prompt(url, page_title, selected_text, active_element, scroll_position):
    return f"""
URL: {url}
Page Title: {page_title}
Selected Text: {selected_text}
Active Element: {active_element}
Scroll Position: {scroll_position}


The user is on the website {url}.

They're going to ask a question specifically about that URL. Use your knowledge of {page_title} to answer.
They want to know literally how to do something on the page. No conceptual answers. Explain using human actions like clicking.
"""