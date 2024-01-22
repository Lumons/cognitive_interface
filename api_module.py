import openai

class APIClient:
    def __init__(self):
        openai.api_base = "http://localhost:1234/v1"
        openai.api_key = ""

        self.client = openai.ChatCompletion()
        self.history = []

    def set_history(self, history):
        self.history = history

    def send_request(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        try:
            completion = self.client.create(
                model="local-model",
                messages=self.history,
                temperature=0.7,
                stream=True,
            )

            new_message_content = ""
            for chunk in completion:
                if 'delta' in chunk.choices[0] and 'content' in chunk.choices[0].delta:
                    new_message_content += chunk.choices[0].delta['content']

            if new_message_content:
                self.history.append({"role": "assistant", "content": new_message_content})
                return new_message_content
        except Exception as e:
            return f"Error accessing content: {e}"
        
    def get_history(self):
        # Return the conversation history
        return self.history
