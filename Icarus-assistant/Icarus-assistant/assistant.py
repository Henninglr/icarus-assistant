from ollama import Client

from memory import ConversationMemory


MODEL_NAME = "qwen3:4b-instruct-2507-q4_K_M"
MAX_HISTORY_MESSAGES = 20

SYSTEM_PROMPT = """
You are Icarus, Henning's personal productivity assistant.

Be friendly, practical, and clear.
Help with programming, learning, planning, and organising projects.
Keep responses concise unless more detail is requested.

You currently support text conversation only.
You cannot access calendars, arbitrary files, the internet, or applications.
Never claim to have performed actions you cannot actually perform.
Be honest when you are unsure.

The application saves completed conversations locally.
Recent messages are provided to you, including after a restart.
Older messages may not be included, so do not claim perfect recall.
"""


class Assistant:
    def __init__(self):
        self.client = Client(
            host="http://localhost:11434",
            timeout=180.0,
        )
        self.memory = ConversationMemory()
        self.history = self.memory.load_recent(MAX_HISTORY_MESSAGES)

    def clear_conversation(self):
        self.memory.clear()
        self.history.clear()

    def reply(self, user_message):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.history,
            {"role": "user", "content": user_message},
        ]

        stream = self.client.chat(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            options={"num_ctx": 4096},
        )

        response_parts = []

        for chunk in stream:
            text = chunk.message.content or ""

            if text:
                response_parts.append(text)
                yield text

        full_response = "".join(response_parts)

        if full_response.strip():
            self.memory.save_exchange(user_message, full_response)

            self.history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": full_response},
            ])
            self.history = self.history[-MAX_HISTORY_MESSAGES:]