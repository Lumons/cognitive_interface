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
        
    def send_summary_request(self, content):
        try:
            # Here, a general completion model is used to create a summary.
            # You might want to customize the prompt based on the content and desired summary style.
            summary_completion = openai.Completion.create(
                model="local-model",  # Your custom model
                prompt=f"Please summarize the following information:\n\n{content}",
                max_tokens=150  # Adjust as needed
            )

            # Extracting and returning the summary text
            return summary_completion.choices[0].text.strip()
        except Exception as e:
            return f"Error generating summary: {e}"


    def get_history(self):
        # Return the conversation history
        return self.history
