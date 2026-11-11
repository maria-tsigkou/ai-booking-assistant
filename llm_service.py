#responsible for communicating with the LLM
from openai import OpenAI

#Create a client that communicates with the OpenAI API.
client = OpenAI()

def ask_llm(message: str) -> str:
    """Send a message to the LLM and return its response"""
    #Makes a real HTTP request to OpenAI's API.
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="You are a helpful accomondation booking assistant.",
        input=message,
        max_output_tokens=150,
    )
    return response.output_text

if __name__ == "__main__":
    answer = ask_llm("Hello! What can you help me with?")
    print(answer)