import os
import re
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
from typing import List, Dict

# Download stopwords if not already downloaded
nltk.download('stopwords')
STOP_WORDS = set(stopwords.words('english'))

class SearchEngine:
    def __init__(self, folder_path: str):
        """Initialize with the folder path containing documents."""
        self.folder_path = folder_path
        self.title_index = defaultdict(list)
        self.content_index = defaultdict(list)
        self.documents = {}

    def load_documents_and_index(self) -> None:
        """Load all documents from the folder and index their titles and contents."""
        for doc_id, filename in enumerate(os.listdir(self.folder_path)):
            file_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    title = file.readline().strip()       # Assume first line is the title
                    content = file.read().strip()         # Remaining content
                    self.documents[doc_id] = {"title": title, "content": content}
                    self.index_document_helper(doc_id, title, content)

    def index_document_helper(self, doc_id: int, title: str, content: str) -> None:
        """Index the words in the title and content of a document."""

        # Process and index title words
        title_words = self._filter_words(re.findall(r'\w+', title.lower()))
        for word in title_words:
            self.title_index[word].append(doc_id)

        # Process and index content words
        content_words = self._filter_words(re.findall(r'\w+', content.lower()))
        for word in content_words:
            self.content_index[word].append(doc_id)

    def _filter_words(self, words: List[str]) -> List[str]:
        """Filter out stopwords from a list of words."""
        return [word for word in words if word not in STOP_WORDS]

    def search(self, query: str, search_by: str) -> List[int]:
        """Perform a search on indexed documents by title or content."""

        query_words = self._filter_words(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        index = self.title_index if search_by == "title" else self.content_index

        result_docs = set(index[query_words[0]])
        for word in query_words[1:]:
            result_docs &= set(index[word])

        return list(result_docs)

    def display_results(self, doc_ids: List[int], search_by: str) -> None:
        """Display the search results."""
        if not doc_ids:
            print("No matching documents found.")
            return

        for doc_id in doc_ids:
            title = self.documents[doc_id]["title"]
            content_snippet = self.documents[doc_id]["content"][:200]  # Show the first 200 characters
            print(f"Document ID: {doc_id + 1}")
            print(f"Title: {title}")
            if search_by == "content":
                print(f"Content: {content_snippet}...")
            print()

    def test_search_engine(self, queries: List[str], search_by: str) -> None:
        """Run a set of test queries."""
        for query in queries:
            print(f"Query: '{query}' (Search by: {search_by})")
            result_docs = self.search(query, search_by)
            self.display_results(result_docs, search_by)


def main():
    """Main entry point for the search engine."""
    folder_path = 'documents'
    search_engine = SearchEngine(folder_path)
    search_engine.load_documents_and_index()
    
    print("Welcome to the Simple Document Search Engine!")
    while True:
        search_by = input("\nWould you like to search by 'title' or 'content'? (type 'exit' to quit): ").strip().lower()
        if search_by == 'exit':
            print("Terminating the session....")
            break
        elif search_by not in {'title', 'content'}:
            print("Invalid option. Please enter 'title' or 'content'.")
            continue

        query = input("Enter search query: ").strip()
        result_docs = search_engine.search(query, search_by)
        search_engine.display_results(result_docs, search_by)


if __name__ == "__main__":
    main()
