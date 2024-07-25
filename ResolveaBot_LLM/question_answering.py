import openai
import wikipediaapi

# Initialize OpenAI API key
openai.api_key = "your_openai_api_key"

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia('en', user_agent="YourAppName/1.0 (your.email@example.com)")

def get_answer_from_llm(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred while generating an answer from the LLM: {e}"

def get_wikipedia_summary(query):
    try:
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary
        else:
            return "No Wikipedia page found for this query."
    except Exception as e:
        return f"An error occurred while fetching from Wikipedia: {e}"

# Combine the query results into a prompt for the LLM
context = " ".join(result['content'] for result in result)  
question = "What is the main topic of the textbook?"

if context.strip() == "":
    # If no local context is available, use Wikipedia
    wikipedia_summary = get_wikipedia_summary(question)
    prompt = f"Based on the following Wikipedia summary, answer the question:\n\n{wikipedia_summary}\n\nQuestion: {question}"
else:
    # Use local context
    prompt = f"Based on the following text, answer the question:\n\n{context}\n\nQuestion: {question}"

# Get the answer from the LLM
answer = get_answer_from_llm(prompt)

# Print the answer
print("Answer:", answer)
