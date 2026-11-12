import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY was not found.")
    exit()

print("API key found.")
print("Connecting to Gemini...")


client = genai.Client(api_key=api_key)


try:
    response = client.interactions.create(
        model="gemini-3.8-flash",
        input="Say hello in one short sentence."
    )

    print("\nGemini response:")
    print(response.output_text)

except Exception as error:
    print("\nGemini connection failed:")
    print(error)