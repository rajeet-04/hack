import requests
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from emb import EmbeddingFunction

CHROMA_PATH = "chroma"

# English greetings database
english_greetings_database = [
    {
        "category": "Formal Greetings",
        "greetings": [
            "Good morning",
            "Good afternoon",
            "Good evening",
            "How do you do?",
            "It's lovely to meet you",
            "Lovely to meet you",
            "Greetings",
            "Pleased to meet you"
        ]
    },
    {
        "category": "Informal Greetings",
        "greetings": [
            "Hello",
            "Hi",
            "Hey",
            "How are you?",
            "How's it going?",
            "How are you doing?",
            "Nice to see you",
            "Good to see you",
            "It's great to see you",
            "Long-time no see",
            "It's been a while",
            "What's up?",
            "What's new?",
            "How's everything?",
            "How's life?",
            "How's life treating you?",
            "Hi there!",
            "Alright?",
            "Alright, mate?",
            "Hiya!"
        ]
    },
    {
        "category": "Slang/Very Informal Greetings",
        "greetings": [
            "Yo!",
            "Heyyy",
            "Sup",
            "What's the craic?",
            "Howdy"
        ]
    },
    {
        "category": "Funny/Uncommon Greetings",
        "greetings": [
            "Ahoy!",
            "Ello, gov'nor!",
            "Goodmorrow!",
            "What's crackin'?",
            "What's up buttercup?",
            "Hello stranger!"
        ]
    }
]

# Check for non-useful content
def is_empty_content(text: str) -> bool:
    return text.strip() == "" or set(text.strip()) == {"\x0c"}

# Determine the type of greeting from the query
def detect_greeting_type(query: str) -> str:
    for category in english_greetings_database:
        if query.lower().strip() in [greeting.lower() for greeting in category["greetings"]]:
            return category["category"]
    return ""

# Generate an appropriate response based on greeting type
def generate_greeting_response(greeting_type: str) -> str:
    responses = {
        "Formal Greetings": "GIVE A FORMAL GREETING",
        "Informal Greetings": "GIVE A INFORMAL GREETING",
        "Slang/Very Informal Greetings": "GIVE A SLANG/VERY INFORMAL GREETING",
        "Funny/Uncommon Greetings": "GIVE A FUNNY/UNCOMMON GREETING",
    }

    return responses.get(greeting_type, "")

# Query the RAG system and fetch context
def query_rag(query_text: str):
    # Check if the query is a greeting
    greeting_type = detect_greeting_type(query_text)
    if greeting_type:
        return ChatPromptTemplate.from_template("""
        {greeting_response}
        """).format(greeting_response=generate_greeting_response(greeting_type))

    # Prepare the DB
    embedding_function = EmbeddingFunction()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=5)

    if not results:
        print("No relevant documents found.")
        return ChatPromptTemplate.from_template("""
        I couldn't find any relevant information. What specific question do you have?
        """)

    # Prepare context from documents
    context_text = "\n\n---\n\n".join(
        [doc.page_content for doc, _ in results if not is_empty_content(doc.page_content)]
    )

    # If all context content is empty, fallback to returning a question prompt
    if not context_text.strip():
        print("All retrieved content is empty. Prompting for user question.")
        return ChatPromptTemplate.from_template("""
        I couldn't find any relevant information. What specific question do you have?
        """)

    # Build prompt
    prompt_template = ChatPromptTemplate.from_template(
        """
        Answer the question based on the following context:

        {context}

        ---

        Answer the question based on the above context: {question}
        """
    )

    # Construct the prompt
    prompt = prompt_template.format(context=context_text, question=query_text)

    return prompt

# Send the prompt to the local server
def send_to_local_server(prompt):
    # Prepare the JSON body for the request
    json_body = {"stream":False,"n_predict":400,"temperature":0.7,"stop":["</s>","Llama:","User:"],"repeat_last_n":256,"repeat_penalty":1.18,"top_k":40,"top_p":0.95,"min_p":0.05,"tfs_z":1,"typical_p":1,"presence_penalty":0,"frequency_penalty":0,"mirostat":0,"mirostat_tau":5,"mirostat_eta":0.1,"grammar":"","n_probs":0,"min_keep":0,"image_data":[],"cache_prompt":False,"api_key":"","slot_id":-1,
                 "prompt":prompt}

    headers = {
        "accept-language": "en-US,en",
        "cache-control": "no-cache",
        "content-type": "application/json"
    }

    try:
        response = requests.post("http://127.0.0.1:8080/completion", json=json_body, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error connecting to the local server: {e}")
        return None

# Main program entry
if __name__ == "__main__":
    while True:
        inp = input('Enter your query (or type "exit" to quit): ')

        if inp.lower() == "exit":
            break

        print(f"Processing query: {inp}")

        # Step 1: Perform RAG to retrieve relevant context
        rag_prompt = query_rag(inp)
        if not rag_prompt:
            print("No relevant context found for the query.")
            continue

        # Step 2: Send the generated prompt to the local server
        response = send_to_local_server(rag_prompt)

        # Parse the response
        if response and response.status_code == 200:
            response_text = response.json().get('content', '')
            print(f"Response: {response_text}")
        else:
            print("Failed to get a valid response from the local server.")