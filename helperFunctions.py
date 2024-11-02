import openai

# Function to prettify chunks into a readable format 
def chunk_text_with_openai(result, chunk_size=750):

    # Prompt instructing GPT-3.5 to chunk text
    prompt = (
        f"Please format the result into readable chunks of {chunk_size} characters inside the output array. Display elements in the array on new lines. Don't add \n, and keep paragraphs following the same header in the same chunk"
        f"{result}"
    )

    # Call OpenAI API with GPT-3.5
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that formats the {result} into readable chunks in the output array"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=750,
    )

    # Process the response
    chunks = response['choices'][0]['message']['content'].strip()

    return chunks

# Splitting array and prettifying chunks using chunk_text_with_openai to process and format chunks properly
def split_array_by_length_with_llm(output, arr, max_length):
    current_chunk = []
    current_length = 0

    for item in arr:
        # Making sure we pass in a string rather than a set/list to the chunk_text_with_openai function 
        if isinstance(item, list):
            item = " ".join(map(str, item))
        
        # Check if adding the current item exceeds the max length
        if current_length + len(item) > max_length:
            formatted_chunks = chunk_text_with_openai(" ".join(current_chunk))

            # Add chunks to output array
            output.extend(formatted_chunks) 

            # Reset the chunk and length counter
            current_chunk = [] 
            current_length = 0

        # Add the current item to the current chunk and update the length
        current_chunk.append(item)
        current_length += len(item)

    # Add the last chunk if it contains items
    if current_chunk:
        formatted_chunks = chunk_text_with_openai(" ".join(current_chunk))
        output.extend(formatted_chunks)

# FEEL FREE TO UNCOMMENT THIS TO RUN CHUNK SPLITTING MANUALLY WITHOUT LLM HELP
# def split_array_by_length(output, arr, max_length):
#     current_chunk = []
#     current_length = 0

#     for item in arr:
        
#         # Check if adding the current item exceeds the max length
#         if current_length + len(item) > max_length:
#             output.append(current_chunk) 

#             # Reset the chunk and length counter
#             current_chunk = []
#             current_length = 0

#         # Add the item to the current chunk and update the length
#         current_chunk.append(item)
#         current_length += len(item)

#     # Add the last chunk if it contains items
#     if current_chunk:
#         output.append(current_chunk)
