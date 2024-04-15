from openai import OpenAI

class APIClient:
    def __init__(self):
        self.client = OpenAI(api_key="lm-studio", base_url="http://localhost:1234/v1")
        self.history = []

    def set_history(self, history):
        self.history = history

    def send_request(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        try:
            completion = self.client.chat.completions.create(
                model="local-model",  # Make sure this is the correct model identifier for your use case
                messages=self.history,
                temperature=0.7
        )

            new_message_content = ""
            # Extract messages from the choices in the completion response
            if completion.choices:
                for choice in completion.choices:
                    # Accessing the message content using dot notation
                    if choice.message.role == 'assistant':
                        new_message_content += choice.message.content

            if new_message_content:
                self.history.append({"role": "assistant", "content": new_message_content})
                return new_message_content
        except Exception as e:
            return f"Error accessing content: {e}"
        
    def send_summary_request(self, content):
        try:
            summary_completion = self.client.chat.completions.create(
                model="local-model",
                prompt=f"Please summarize the following information:\n\n{content}",
                max_tokens=150
            )

            # Adjusting response handling according to the new API structure
            return summary_completion.choices[0].text.strip()
        except Exception as e:
            return f"Error generating summary: {e}"

    def get_history(self):
        return self.history
    