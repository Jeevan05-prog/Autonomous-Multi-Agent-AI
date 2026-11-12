from ddgs import DDGS
from agents.llm import ask_gemini


def create_search_queries(user_request):

    return [

        f"{user_request} statistics and historical trends",

        f"{user_request} latest developments and research",

        f"{user_request} reports and numerical evidence",

        f"{user_request} real world examples and case studies",

        f"{user_request} challenges opportunities and future outlook"

    ]


def researcher_agent(state):

    user_request = state.get("user_request", "")

    print("\n========== RESEARCH AGENT ==========")

    search_queries = create_search_queries(user_request)

    collected_results = []
    visited_urls = set()

    for index, query in enumerate(search_queries, start=1):

        print(f"\nSearch {index}/{len(search_queries)}:")
        print(query)

        try:

            results = DDGS().text(
                query,
                max_results=3
            )

            result_count = 0

            for result in results:

                url = result.get("href", "").strip()

                if not url or url in visited_urls:
                    continue

                visited_urls.add(url)

                collected_results.append({

                    "title": result.get("title", ""),
                    "url": url,
                    "snippet": result.get("body", "")

                })

                result_count += 1

            print(f"Results collected: {result_count}")

        except Exception as error:

            print(f"Search failed: {error}")
            print("Continuing with next search...")

    if not collected_results:

        state["research"] = (
            "No relevant web search results were collected. "
            "Please try again later."
        )

        return state

    research_data = ""

    for index, result in enumerate(collected_results, start=1):

        research_data += f"""

SOURCE {index}

Title: {result['title']}

URL: {result['url']}

Information:
{result['snippet']}

----------------------------------------

"""

    print(
        f"\nTotal unique sources: {len(collected_results)}"
    )

    prompt = f"""

You are an expert research analyst.

The exact research topic is:

{user_request}

Collected web research:

{research_data}

Your task is to prepare a detailed research summary.

Include:

1. Introduction to the topic
2. Background and theoretical concepts
3. Important facts and statistics
4. Historical development
5. Current developments
6. Real-world applications
7. Case studies and examples
8. Major trends
9. Opportunities and challenges
10. Future developments

IMPORTANT RULES:

- Stay strictly focused on the given topic.
- Do not introduce unrelated industries.
- Explain technical terms in simple language.
- Use only facts supported by the collected sources.
- Do not invent statistics.
- Clearly identify information gaps.
- Preserve source URLs.
- Explain the significance of the findings.
- Do not simply copy search snippets.
- Distinguish facts from predictions.

Write detailed paragraphs that a student or general reader can understand.

"""

    try:

        print("\nGenerating research summary using Gemini...")

        summary = ask_gemini(prompt)

        source_register = "\n\nSOURCE REGISTER\n===============\n"

        for index, item in enumerate(collected_results, start=1):

            source_register += (

                f"\nSOURCE {index}: {item['title']}\n"
                f"URL: {item['url']}\n"
                f"Search snippet: {item['snippet']}\n"

            )

        state["research"] = summary + source_register

        print("\nResearch summary generated successfully.")

    except Exception as error:

        print("\nGemini summarization unavailable.")
        print(f"Reason: {error}")

        state["research"] = research_data

    return state