import sqlite3

from httpx import HTTPError
from ollama import ResponseError

from assistant import Assistant, MODEL_NAME


def main():
    try:
        assistant = Assistant()
    except (sqlite3.Error, OSError) as error:
        print(f"Could not open Icarus's memory: {error}")
        return

    print("Icarus is ready.")
    print(f"Local model: {MODEL_NAME}")
    print(f"Loaded {len(assistant.history) // 2} previous exchanges.")
    print("Commands: /clear to delete conversation history, /exit to quit.")

    while True:
        try:
            message = input("\nYou: ").strip()

            if not message:
                continue

            if message.lower() in {"/exit", "exit", "quit"}:
                print("Icarus: Goodbye, Henning.")
                break

            if message.lower() == "/clear":
                confirmation = input(
                    "Delete all saved conversation history? Type yes: "
                ).strip().lower()

                if confirmation == "yes":
                    assistant.clear_conversation()
                    print("Icarus: Saved conversation history cleared.")
                else:
                    print("Icarus: History kept.")

                continue

            print("\nIcarus: ", end="", flush=True)

            try:
                for text in assistant.reply(message):
                    print(text, end="", flush=True)

                print()

            except KeyboardInterrupt:
                print("\nResponse interrupted. This exchange was not saved.")

        except ResponseError as error:
            print(f"\nOllama error: {error.error}")

            if error.status_code == 404:
                print(f"Download the model with: ollama pull {MODEL_NAME}")

        except (ConnectionError, HTTPError) as error:
            print("\nCould not complete the connection to Ollama.")
            print(f"Details: {error}")

        except (sqlite3.Error, OSError) as error:
            print(f"\nStorage error: {error}")
            print("The latest operation may not have been saved.")

        except (KeyboardInterrupt, EOFError):
            print("\nIcarus: Goodbye, Henning.")
            break


if __name__ == "__main__":
    main()