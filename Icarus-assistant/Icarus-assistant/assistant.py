from ollama import Client


MODEL_NAME = "qwen3:4b-instruct-2507-q4_K_M"

SYSTEM_PROMPT = """
You are Icarus, Henning's personal productivity assistant.

Be friendly, practical, and clear.
Help with programming, learning, planning, and organising projects.
Keep responses concise unless more detail is requested.

You currently support text conversation only.
You cannot access calendars, files, the internet, or applications.
Never claim to have performed actions you cannot actually perform.
Be honest when you are unsure.

Your conversation memory lasts only while this program is running.
"""

MAX_HISTORY_MESSAGES = 20


class Assistant:
    def __init__(self):
        self.client = Client(
            host="http://localhost:11434",
            timeout=180.0,
        )
        self.history = []

    def clear_conversation(self):
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

        # Keep completed exchanges only, retaining the latest ten pairs.
        if full_response.strip():
            self.history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": full_response},
            ])
            self.history = self.history[-MAX_HISTORY_MESSAGES:]