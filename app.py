from graph.workflow import create_workflow


def main():

    print("\n==========================================")
    print("     AUTONOMOUS MULTI-AGENT AI SYSTEM")
    print("==========================================")

    user_request = input(
        "\nEnter your research topic: "
    ).strip()

    if not user_request:

        print("Research topic cannot be empty.")

        return

    print("\nProvide an optional CSV dataset.")

    dataset_path = input(
        "Enter CSV path (press Enter to skip): "
    ).strip().strip('"')

    initial_state = {

        "user_request": user_request,

        "plan": [],

        "research": "",

        "dataset_path": dataset_path,

        "analysis": "",

        "insights": "",

        "critique": "",

        "final_report": "",

        "research_round": 0
    }

    print("\nStarting multi-agent workflow...")

    workflow = create_workflow()

    try:

        final_state = workflow.invoke(
            initial_state
        )

        print("\n==========================================")
        print("          WORKFLOW COMPLETED")
        print("==========================================")

        print("\nFINAL INSIGHTS:")
        print(final_state["insights"])

        print("\nCRITIC REVIEW:")
        print(final_state["critique"])

        print("\nFINAL REPORT:")
        print("outputs/final_report.md")

        print("\n==========================================")

    except Exception as error:

        print("\nWORKFLOW ERROR")

        print(error)


if __name__ == "__main__":

    main()