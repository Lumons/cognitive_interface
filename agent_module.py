import openai
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
            # Check if response is successful and a dictionary
            if isinstance(response, dict) and 'choices' in response and len(response['choices']) > 0:
                # Correctly accessing and returning the response text
                response_text = response['choices'][0]['message']['content']
                print(response_text)  # Print the response text for debugging
                return response_text  # Return the response text so it can be used outside this method
            else:
                error_message = "Unexpected response format or empty choices"
                print(error_message, response)
                return error_message  # Return the error message if response is not as expected
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            return error_message  # Return the error message on exception


class Summariser(BaseAgent):
    def __init__(self):
        super().__init__(system_query="You are a summariser, provide a list of the topics covered in this journal entry:")
   
    def process_chunks(self, chunks):
        markdown_output = []
        for index, chunk in enumerate(chunks, start=1):  # Start numbering from 1
            text_content = chunk.page_content
            print("Processing chunk:", text_content[:100])  # Show the beginning of the chunk
            response = self.get_response(text_content)  # Get the response from the API
            print("Response received for chunk:", response)  # Ensure the response is what's expected
        
        # Format the response into a markdown entry
            markdown_entry = f"### Chunk {index} summary:\n```markdown\n{response}\n```\n\n"
            markdown_output.append(markdown_entry)  # Append the formatted markdown to the list
            print("Markdown entry to append:", markdown_entry)  # Debug print to check the markdown entry
        
    def save_to_markdown(self, markdown_output):
        # Define the file path where the markdown file will be saved
        filepath = 'output.md'
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(markdown_output)
        print(f"Markdown file saved successfully at {filepath}")


def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None



if __name__ == "__main__":
    # Define the path to the file directly
    file_path = "C:\\Users\\montu\\repos\\interface\\logs\\2024-04-03-user-contents.txt"
    
    # Read the contents of the file
    file_contents = read_file_contents(file_path)

    custom_text_splitter = RecursiveCharacterTextSplitter(
    # Set custom chunk size
    chunk_size = 1500,
    chunk_overlap  = 200
    )
    chunks = custom_text_splitter.create_documents([file_contents])
    

    summariser = Summariser()
    summariser.process_chunks(chunks)
