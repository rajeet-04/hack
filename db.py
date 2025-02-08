import os
from langchain.schema import Document
from emb import EmbeddingFunction
from langchain_chroma import Chroma
from to_md import convert_to_md


def process_file(file_path: str, chroma_path: str):
    """
    Process a single file, convert it to Markdown, and store it in the Chroma database.

    :param file_path: Path to the document file to be processed.
    :param chroma_path: Path where the Chroma database is stored.
    """

    # Validate file existence
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print("❌ Invalid file path. Please check the path and try again.")
        return

    try:
        # Convert the document to Markdown
        print(f"📄 Converting file: {file_path}")
        md_content = convert_to_md(file_path)

        # Add the Markdown content to the Chroma database
        add_to_chroma([Document(page_content=md_content, metadata={"source": file_path})], chroma_path)
        print(md_content)
        print("✅ File successfully processed and added to the database!")

    except Exception as e:
        print(f"❌ Error processing file {file_path}: {e}")


def add_to_chroma(chunks: list[Document], chroma_path: str):
    """
    Add documents to the Chroma database.

    :param chunks: List of document chunks to be added.
    :param chroma_path: Path for the Chroma database.
    """
    print(f"📦 Loading Chroma database from: {chroma_path}")
    embedding_function = EmbeddingFunction()
    db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    embeddings = embedding_function.embed_documents(texts)

    if not embeddings:
        print("❌ No embeddings generated. Aborting...")
        return

    db.add_texts(texts=texts, metadatas=metadatas)
    print("✅ Documents added successfully!")
    print(texts)


# Example Usage
if __name__ == "__main__":
    file_path = "example_documents/sample.pdf"  # Replace with your file path
    chroma_path = "./chroma_db"  # Path to store the Chroma database

    process_file(file_path, chroma_path)
