from db.context_docs import get_relevant_context_docs, get_relevant_images
from typing import List, Dict

def get_system_prompt(organization_id, url, page_title, selected_text, active_element, scroll_position) -> List[Dict]:
    relevant_docs = get_relevant_context_docs(organization_id, url)
    relevant_images = get_relevant_images(organization_id, url)
    context_docs_text = "\n\n".join([f"Document Name: {doc['document_name']}\nDocument Text: {doc['document_text']}" for doc in relevant_docs]) if relevant_docs else ""

    main_prompt = f"""
URL: {url}
Page Title: {page_title}
Selected Text: {selected_text}
Active Element: {active_element}
Scroll Position: {scroll_position}


Be concise. Give only 1-2 sentence answers.
Don't make things up. Only answer based on the context provided.


So give answers confidently. Don't say "Based on the context provided" or anything like that.
Be helpful and friendly.
Continue with 1-2 short sentences of the answer.

<SiteSpecificContext>
{context_docs_text}
</SiteSpecificContext>

"""

    prompt_array = [{"type": "text", "content": main_prompt}]
    
    for image in relevant_images:
        prompt_array.append({
            "type": "image",
            "image_base64": image['image_base64'],
            "image_name": image['document_name']
#            "type": "image_url",
#            "document_name": image['document_name'],
#            "image_url": {
#                "url": f"data:image/jpeg;base64,{image['image_base64']}"
#            }
        })

    return prompt_array