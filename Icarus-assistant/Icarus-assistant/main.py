from httpx import HTTPError
from ollama import ResponseError

from assistant import Assistant, MODEL_NAME


def main():
    assistant = Assistant()

    print("Icarus is ready.")
    print(f"Local model: {MODEL_NAME}")
    print("Commands: /clear to reset the conversation, /exit to quit.")
    print("The first response may take longer while the model loads.")

    while True:
        try:
            message = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nIcarus: Goodbye, Henning.")
            break

        if not message:
            continue

        if message.lower() in {"/exit", "exit", "quit"}:
            print("Icarus: Goodbye, Henning.")
            break

        if message.lower() == "/clear":
            assistant.clear_conversation()
            print("Icarus: Conversation cleared.")
            continue

        print("\nIcarus: ", end="", flush=True)

        try:
            for text in assistant.reply(message):
                print(text, end="", flush=True)

            print()

        except ResponseError as error:
            print(f"\nOllama error: {error.error}")

            if error.status_code == 404:
                print(f"Download the model with: ollama pull {MODEL_NAME}")

        except (ConnectionError, HTTPError) as error:
            print("\nCould not complete the connection to Ollama.")
            print("Check that Ollama is running, then try again.")
            print(f"Details: {error}")

        except KeyboardInterrupt:
            print("\nResponse interrupted. This exchange was not saved.")


if __name__ == "__main__":
    main()