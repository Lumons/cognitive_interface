import openai
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class BaseAgent:
    def __init__(self, model_name="local-model", system_query="Define the role and task for this agent."):
        openai.api_key = "lm-studio"  # Ensure this is your actual API key
        openai.api_base = "http://localhost:1234/v1"
        self.model = model_name
        self.system_query = system_query


    def get_response(self, user_query):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_query},
                    {"role": "user", "content": user_query}
                ]
            )
            if isinstance(response, dict) and 'choices' in response and len(response['choices']) > 0:
                response_text = response['choices'][0]['message']['content']
                return response_text
            else:
                return "Unexpected response format or empty choices"
        except Exception as e:
            return f"An error occurred: {e}"

class Summariser(BaseAgent):
    def __init__(self):
        super().__init__(system_query="Return nothing but a list of the topics covered in this journal entry:")

    def process_chunks(self, chunks):
        markdown_output = ["## Summary\n"]
        for index, chunk in enumerate(chunks, start=1):
            text_content = chunk.page_content
            response = self.get_response(text_content)
            markdown_entry = f"### Chunk {index} summary:\n{response}\n\n"
            markdown_output.append(markdown_entry)
        return markdown_output

    def save_to_markdown(self, markdown_output, filepath):
        mode = 'a' if os.path.exists(filepath) else 'w'
        with open(filepath, mode, encoding='utf-8') as file:
            file.writelines(markdown_output)
        print(f"Markdown file updated successfully at {filepath}")

class PeopleFinder(BaseAgent):
    def __init__(self):
        super().__init__(system_query="Return nothing but a list of names mentioned in this journal entry:")

    def process_chunks(self, chunks):
        markdown_output = ["## Summary\n"]
        for index, chunk in enumerate(chunks, start=1):
            text_content = chunk.page_content
            response = self.get_response(text_content)
            markdown_entry = f"### Chunk {index} summary:\n{response}\n\n"
            markdown_output.append(markdown_entry)
        return markdown_output

    def save_to_markdown(self, markdown_output, filepath):
        mode = 'a' if os.path.exists(filepath) else 'w'
        with open(filepath, mode, encoding='utf-8') as file:
            file.writelines(markdown_output)
        print(f"Markdown file updated successfully at {filepath}")

def read_file_contents(file_path):
    try:
        print(f"Trying to open the file: {os.path.abspath(file_path)}")
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            print(f"Successfully read {len(contents)} characters from the file.")
            return contents
    except Exception as e:
        print(f"Error reading file: {os.path.abspath(file_path)} - {e}")
        return None

if __name__ == "__main__":
    file_path = "logs/2024-02-08T12-43-36+0000-Log-entry-1.json"
    markdown_file_path = "output.md"
    file_contents = read_file_contents(file_path)
    custom_text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=250)
    chunks = custom_text_splitter.create_documents([file_contents])
    summariser = Summariser()
    markdown_content = summariser.process_chunks(chunks)
    summariser.save_to_markdown(markdown_content, markdown_file_path)
    peoplefinder = PeopleFinder()
    markdown_content = peoplefinder.process_chunks(chunks)
    peoplefinder.save_to_markdown(markdown_content, markdown_file_path)
