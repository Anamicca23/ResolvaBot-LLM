from unittest import result
import openai


# Initialize OpenAI API key
openai.api_key = "your_openai_api_key"

def get_answer_from_llm(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Combine the query results into a prompt for the LLM
context = " ".join(result['content'] for result in result)
question = "What is the main topic of the textbook?"
prompt = f"Based on the following text, answer the question:\n\n{context}\n\nQuestion: {question}"

# Get the answer from the LLM
answer = get_answer_from_llm(prompt)

# Print the answer
print("Answer:", answer)
