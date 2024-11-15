import os
import re
# import nltk
# from nltk.corpus import stopwords
# from collections import defaultdict
from typing import List, Dict

# Download stopwords if not already downloaded
# nltk.download('stopwords')

class HashMapEntry:
    """Represents a key-value pair in the custom hash map."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.is_active = True

class CustomHashMap:
    def __init__(self, initial_capacity=8, load_factor_threshold=0.7):
        self.capacity = initial_capacity
        self.size = 0
        self.load_factor_threshold = load_factor_threshold
        self.table = [None] * self.capacity

    def _hash(self, key):
        return hash(key) % self.capacity

    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size = 0

        for entry in old_table:
            if entry and entry.is_active:
                self.set(entry.key, entry.value)

    def set(self, key, value):
        if self.size / self.capacity > self.load_factor_threshold:
            self._resize()

        index = self._hash(key)
        while self.table[index] is not None:
            entry = self.table[index]
            if entry.key == key and entry.is_active:
                entry.value = value
                return
            index = (index + 1) % self.capacity

        self.table[index] = HashMapEntry(key, value)
        self.size += 1

    def get(self, key):
        index = self._hash(key)
        while self.table[index] is not None:
            entry = self.table[index]
            if entry.key == key and entry.is_active:
                return entry.value
            index = (index + 1) % self.capacity
        return None

    def contains(self, key):
        index = self._hash(key)
        while self.table[index] is not None:
            entry = self.table[index]
            if entry.key == key and entry.is_active:
                return True
            index = (index + 1) % self.capacity
        return False

    def __repr__(self):
        return "{" + ", ".join(f"{entry.key}: {entry.value}" for entry in self.table if entry and entry.is_active) + "}"


STOP_WORDS = set({'ours', 'just', 'hasn', 'they', "weren't", 'its', "won't", 'down', 
                  'when', 'it', 'd', 'a', 'further', 'during', 'm', 'who', 'my',
                  'them', "didn't", 'being', 'or', "she's", 'your', 'against', 
                  'didn', 'were', 'can', 'than', 'into', 'under', 'isn', 
                  'been', 'any', 'hadn', 'from', 'myself', 'not', 'then', 
                  "don't", 'most', 'the', 'o', 've', 'very', 'because', 
                  'are', 'their', "hasn't", 'both', 'doing', 'needn', 
                  'itself', 'don', 'on', 'here', 'of', 'few', 's', 'hers', 
                  'while', "haven't", 'whom', 'such', 'aren', 'herself', 
                  "hadn't", 'yours', 'shouldn', 'ourselves', 'be', "you're", 
                  'why', 'me', 'as', 'an', 'y', 'is', 'each', 'haven', 'mightn', 
                  'wouldn', 'shan', 'ma', 'if', 'couldn', 're', 'her', "doesn't", 
                  'through', 'and', 'doesn', 'this', 'own', 'again', 'no', 'had', 
                  'ain', 'up', 'will', 'having', 'where', 'in', 'off', 'by', 't', 
                  'was', "that'll", 'before', 'out', 'there', 'have', 'weren', 
                  'over', 'so', 'did', "you'll", 'we', 'same', "it's", 'you', 
                  'too', "should've", 'about', 'these', 'how', 'now', 'themselves', 
                  "shan't", 'she', 'more', 'after', "couldn't", 'above', 'which', 
                  'all', "shouldn't", "wouldn't", 'at', "needn't", 'but', 'that', 
                  "you've", 'only', 'does', 'once', 'between', "mightn't", 'to', 
                  'won', 'theirs', "isn't", 'with', 'other', 'his', 'until', 'mustn', 
                  "you'd", 'do', 'for', 'yourself', "mustn't", 'himself', 'some', 'has', 
                  'nor', 'yourselves', 'he', 'should', 'him', "wasn't", 'below', "aren't", 
                  'those', 'am', 'wasn', 'our', 'what', 'll', 'i'})

class SearchEngine:
    def __init__(self, folder_path: str):
        """Initialize with the folder path containing documents."""
        self.folder_path = folder_path
        self.title_index = CustomHashMap()
        self.content_index = CustomHashMap()
        self.documents = CustomHashMap()

    def load_documents_and_index(self) -> None:
        """Load all documents from the folder and index their titles and contents."""
        print("Indexing of the documents has started!\n")
        for doc_id, filename in enumerate(os.listdir(self.folder_path)):
            file_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    title = file.readline().strip()       # Assume first line is the title
                    content = file.read().strip()         # Remaining content
                    self.documents.set(doc_id, {"title": title, "content": content})
                    self.index_document_helper(doc_id, title, content)

    def index_document_helper(self, doc_id: int, title: str, content: str) -> None:
        """Index the words in the title and content of a document."""

        # Process and index title words
        title_words = self._filter_words(re.findall(r'\w+', title.lower()))
        for word in title_words:
            if not self.title_index.contains(word):
                self.title_index.set(word, [])
            self.title_index.get(word).append(doc_id)

        # Process and index content words
        content_words = self._filter_words(re.findall(r'\w+', content.lower()))
        for word in content_words:
            if not self.content_index.contains(word):
                self.content_index.set(word, [])
            self.content_index.get(word).append(doc_id)

    def _filter_words(self, words: List[str]) -> List[str]:
        """Filter out stopwords from a list of words."""
        return [word for word in words if word not in STOP_WORDS]

    def search(self, query: str, search_by: str) -> List[int]:
        """Perform a search on indexed documents by title or content."""

        query_words = self._filter_words(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        index = self.title_index if search_by == "title" else self.content_index

        result_docs = set(index.get(query_words[0]) or [])
        for word in query_words[1:]:
            result_docs |= set(index.get(word) or [])

        return list(result_docs)

    def display_results(self, doc_ids: List[int], search_by: str) -> None:
        """Display the search results."""
        if not doc_ids:
            print("No matching documents found.")
            return

        for doc_id in doc_ids:
            title = self.documents.get(doc_id)["title"]
            content_snippet = self.documents.get(doc_id)["content"][:200]
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

# User Interface in comand line
def Search_Engine_UI(search_engine):
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


def main():
    """Main entry point for the search engine."""
    folder_path = 'documents'
    search_engine = SearchEngine(folder_path)
    search_engine.load_documents_and_index()
    
    Search_Engine_UI(search_engine)
    

if __name__ == "__main__":
    main()
