import os
import time
import requests

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )


# Gemini configuration
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

MODEL_NAME = "gemini-3.6-flash"


def ask_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini using the REST API.
    Retries temporary server errors.
    """

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    payload = {
        "model": MODEL_NAME,
        "input": prompt,
    }

    max_retries = 4

    for attempt in range(max_retries):

        try:
            response = requests.post(
                GEMINI_URL,
                headers=headers,
                json=payload,
                timeout=90,
            )

            if response.status_code in [500, 502, 503, 504]:

                if attempt < max_retries - 1:

                    wait_time = 5 * (attempt + 1)

                    print(
                        f"\nGemini temporarily unavailable "
                        f"(HTTP {response.status_code})."
                    )

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

            response.raise_for_status()

            result = response.json()

            # Extract generated text
            for step in result.get("steps", []):

                if step.get("type") == "model_output":

                    for content in step.get("content", []):

                        if content.get("type") == "text":

                            return content.get("text", "")

            raise RuntimeError(
                "Gemini response did not contain generated text."
            )

        except requests.exceptions.Timeout:

            if attempt < max_retries - 1:

                wait_time = 5 * (attempt + 1)

                print("\nGemini request timed out.")

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            raise RuntimeError(
                "Gemini request timed out after multiple attempts."
            )

        except requests.exceptions.RequestException as error:

            raise RuntimeError(
                f"Gemini API request failed: {error}"
            )

    raise RuntimeError(
        "Gemini request failed after multiple attempts."
    )