#responsible for communicating with the LLM
from openai import OpenAI
from openai.types.responses import FunctionToolParam
from datetime import date
from booking import search_properties
from fastapi.encoders import jsonable_encoder
import json

#Create a client that communicates with the OpenAI API.
client = OpenAI()

PROPERTY_SEARCH_TOOL: FunctionToolParam = {
    "type": "function",
    "name": "search_properties",
    "description": (
        "Search available accomodation properties "
        "for a given number of guests and booking dates."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "guests": {
                "type": "integer",
                "description": "Number of guests"
            },
            "check_in": {
                "type": "string",
                "description": "Check-in date in YYYY-MM-DD format"
            },
            "check_out":{
                "type": "string",
                "description": "Check-out date in YYYY-MM-DD format"
            }
        },
        "required": [
            "guests",
            "check_in",
            "check_out"
        ],
        "additionalProperties": False
    },
    "strict": True
}

def ask_llm(message: str) -> str:
    """Send a message to the LLM and return its response"""
    #Makes a real HTTP request to OpenAI's API.
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="You are a helpful accomodation booking assistant.",
        input=message,
        tools=[PROPERTY_SEARCH_TOOL],
        max_output_tokens=150,
    )
    tool_outputs  = []
    for item in response.output:
        if item.type == "function_call":
            if item.name != "search_properties":
                raise ValueError("Unknown tool requested")
            
            arguments = json.loads(item.arguments)

            guests = arguments["guests"]
            check_in = date.fromisoformat(arguments["check_in"])
            check_out = date.fromisoformat(arguments["check_out"])

            results = search_properties(
                guests=guests,
                check_in=check_in,
                check_out=check_out
            )
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(jsonable_encoder(results))
            })

    if not tool_outputs:
        return response.output_text

    final_response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a helpful accommodation booking assistant. "
            "Use only the provided property search results. "
            "Do not invent properties, prices, or currencies."
        ),
        previous_response_id=response.id,
        input=tool_outputs,
        max_output_tokens=250,
    )
            
    return final_response.output_text

if __name__ == "__main__":
    answer = ask_llm("Find accomodation for 2 guests from December 10 to December 15, 2027.")
    print("AI ANSWER:",answer)