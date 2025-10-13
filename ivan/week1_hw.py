"""
Week 1 Homework - DataTalks.Club Podcasts Archive

HOW TO RUN:
===========
From the project root directory:
  uv run python ivan/week1_hw.py

Or if you have the environment activated:
  python ivan/week1_hw.py

Requirements:
  - requests
  - python-frontmatter
  - minsearch

Data Source: https://github.com/DataTalksClub/datatalksclub.github.io/tree/main/_podcast

HINTS & REFERENCE FILES:
========================
This homework is based on the patterns from week1 folder:
- week1/docs.py - GithubRepositoryDataReader class, parse_data(), chunk_documents()
- week1/docs.ipynb - Full workflow with frontmatter parsing and sliding window chunking
- week1/youtube.ipynb - Alternative sliding window implementation for transcript chunking

QUESTIONS AND ANSWERS:
======================

Question 4: Download the podcast data (only for podcasts). How many records are there?
Answer: 185 records
Summary: Downloaded all files from the _podcast directory in the DataTalksClub repository
Approach:
  - Created GithubRepositoryDataReader class to download GitHub repo as ZIP
  - Filtered files by path prefix (_podcast)
  - Extracted and counted all podcast files
  - Result: 185 podcast records including markdown files for each episode
Reference: week1/docs.py (lines 18-172), week1/docs.ipynb (GithubRepositoryDataReader class)

Question 5: Prepare the data using paragraphs with chunk size 30 and overlap 15. How many chunks?
Answer: 162 chunks
Summary: Parse podcast markdown files using frontmatter, then chunk by paragraphs with sliding window
Approach:
  - Parse frontmatter from markdown files to extract metadata and content (184 valid files)
  - Split content by paragraphs (double newlines)
  - Use sliding window with size=30 paragraphs, step=15 paragraphs (overlap=15)
  - Result: 162 total chunks created from all podcast documents
Reference: week1/docs.py (lines 189-280), week1/docs.ipynb (parse_data, sliding_window, chunk_documents)
          week1/youtube.ipynb (alternative sliding_window implementation)

Question 6: Index the data with minsearch. What's the first episode in results for "how do I make money with AI?"
Answer: s13e06-secret-sauce-of-data-science-management.md
Summary: Use minsearch Index to index chunks and search for relevant content
Approach:
  - Create Index with text_fields=["content"] for searchable content
  - Fit the index with the 162 chunks
  - Search for the query "how do I make money with AI?"
  - First result: _podcast/s13e06-secret-sauce-of-data-science-management.md
Reference: week1/docs.ipynb (Index usage), week1/rag.py (minsearch Index setup)

"""

import io
import zipfile
from dataclasses import dataclass
from typing import Any, Dict, List

import requests
import frontmatter
from minsearch import Index


@dataclass
class RawRepositoryFile:
    filename: str
    content: str


class GithubRepositoryDataReader:
    """
    Downloads and parses files from a GitHub repository.
    """

    def __init__(self,
                 repo_owner: str,
                 repo_name: str,
                 allowed_extensions: set[str] | None = None,
                 path_filter: str | None = None):
        """
        Initialize the GitHub repository data reader.

        Args:
            repo_owner: The owner/organization of the GitHub repository
            repo_name: The name of the GitHub repository
            allowed_extensions: Optional set of file extensions to include
            path_filter: Optional path prefix to filter files (e.g., "_podcast")
        """
        prefix = "https://codeload.github.com"
        self.url = f"{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main"

        self.allowed_extensions = allowed_extensions
        self.path_filter = path_filter

    def read(self) -> list[RawRepositoryFile]:
        """
        Download and extract files from the GitHub repository.

        Returns:
            List of RawRepositoryFile objects for each processed file
        """
        resp = requests.get(self.url)
        if resp.status_code != 200:
            raise Exception(f"Failed to download repository: {resp.status_code}")

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        repository_data = self._extract_files(zf)
        zf.close()

        return repository_data

    def _extract_files(self, zf: zipfile.ZipFile) -> list[RawRepositoryFile]:
        """
        Extract and process files from the zip archive.

        Args:
            zf: ZipFile object containing the repository data

        Returns:
            List of RawRepositoryFile objects for each processed file
        """
        data = []

        for file_info in zf.infolist():
            filepath = self._normalize_filepath(file_info.filename)

            if self._should_skip_file(filepath):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode("utf-8", errors="ignore")
                    if content is not None:
                        content = content.strip()

                    file = RawRepositoryFile(
                        filename=filepath,
                        content=content
                    )
                    data.append(file)

            except Exception as e:
                print(f"Error processing {file_info.filename}: {e}")
                continue

        return data

    def _should_skip_file(self, filepath: str) -> bool:
        """
        Determine whether a file should be skipped during processing.

        Args:
            filepath: The file path to check

        Returns:
            True if the file should be skipped, False otherwise
        """
        # Skip directories
        if filepath.endswith("/"):
            return True

        # Skip hidden files
        filename = filepath.split("/")[-1]
        if filename.startswith("."):
            return True

        # Filter by path prefix if specified
        if self.path_filter and not filepath.startswith(self.path_filter):
            return True

        # Filter by extension if specified
        if self.allowed_extensions:
            ext = self._get_extension(filepath)
            if ext not in self.allowed_extensions:
                return True

        return False

    def _get_extension(self, filepath: str) -> str:
        """
        Extract the file extension from a filepath.

        Args:
            filepath: The file path to extract extension from

        Returns:
            The file extension (without dot) or empty string if no extension
        """
        filename = filepath.lower().split("/")[-1]
        if "." in filename:
            return filename.rsplit(".", maxsplit=1)[-1]
        else:
            return ""

    def _normalize_filepath(self, filepath: str) -> str:
        """
        Removes the top-level directory from the file path inside the zip archive.
        'repo-main/path/to/file.py' -> 'path/to/file.py'

        Args:
            filepath: The original filepath from the zip archive

        Returns:
            The normalized filepath with top-level directory removed
        """
        parts = filepath.split("/", maxsplit=1)
        if len(parts) > 1:
            return parts[1]
        else:
            return parts[0]


def download_podcast_data():
    """
    Question 4: Download podcast data from DataTalks.Club GitHub repository.

    Returns:
        List of RawRepositoryFile objects containing podcast data
    """
    repo_owner = 'DataTalksClub'
    repo_name = 'datatalksclub.github.io'

    # Only get files from _podcast directory
    reader = GithubRepositoryDataReader(
        repo_owner,
        repo_name,
        path_filter="_podcast"
    )

    data = reader.read()
    return data


def parse_podcast_data(data_raw):
    """
    Parse markdown files with frontmatter to extract metadata and content.

    Args:
        data_raw: List of RawRepositoryFile objects

    Returns:
        List of parsed dictionaries with filename, metadata, and content
    """
    data_parsed = []
    for f in data_raw:
        try:
            post = frontmatter.loads(f.content)
            data = post.to_dict()
            data['filename'] = f.filename
            data_parsed.append(data)
        except Exception as e:
            # Skip files with parsing errors (like templates)
            print(f"Skipping {f.filename}: {type(e).__name__}")
            continue

    return data_parsed


def sliding_window(seq: List[Any], size: int, step: int) -> List[Dict[str, Any]]:
    """
    Create overlapping chunks from a sequence using a sliding window approach.

    Args:
        seq: The input sequence (list of paragraphs) to be chunked
        size: The size of each chunk/window (number of paragraphs)
        step: The step size between consecutive windows

    Returns:
        List of dictionaries, each containing:
            - 'start': The starting position of the chunk
            - 'content': The chunk content (joined paragraphs)
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []

    for i in range(0, n, step):
        batch = seq[i:i+size]
        # Join paragraphs back with double newlines
        content = '\n\n'.join(batch)
        result.append({'start': i, 'content': content})
        if i + size >= n:
            break

    return result


def chunk_documents_by_paragraphs(
    documents: List[Dict[str, Any]],
    size: int = 30,
    step: int = 15,
    content_field_name: str = 'content'
) -> List[Dict[str, Any]]:
    """
    Split documents into chunks by paragraphs using sliding windows.

    Args:
        documents: List of document dictionaries with content field
        size: Number of paragraphs per chunk (default: 30)
        step: Step size between chunks (default: 15, creates overlap of size-step)
        content_field_name: Name of the field containing document content

    Returns:
        List of chunk dictionaries with metadata preserved
    """
    results = []

    for doc in documents:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop(content_field_name, '')

        # Skip if no content
        if not doc_content:
            continue

        # Split content by paragraphs (double newlines)
        paragraphs = doc_content.split('\n\n')
        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Create chunks using sliding window
        chunks = sliding_window(paragraphs, size=size, step=step)

        # Add document metadata to each chunk
        for chunk in chunks:
            chunk.update(doc_copy)

        results.extend(chunks)

    return results


def search_podcasts(chunks, query, num_results=5):
    """
    Search podcast chunks using minsearch.

    Args:
        chunks: List of chunk dictionaries
        query: Search query string
        num_results: Number of results to return

    Returns:
        List of search results
    """
    # Create index with content as the main text field
    index = Index(text_fields=["content"])

    # Fit the index with chunks
    index.fit(chunks)

    # Search for the query
    results = index.search(query=query, num_results=num_results)

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Question 4: Downloading podcast data from DataTalks.Club...")
    print("=" * 70)
    podcast_files = download_podcast_data()

    print(f"\nNumber of podcast records: {len(podcast_files)}")

    # Show a few example filenames
    print("\nExample filenames:")
    for i, file in enumerate(podcast_files[:5]):
        print(f"  {i+1}. {file.filename}")

    print("\n" + "=" * 70)
    print("Question 5: Chunking podcast data by paragraphs...")
    print("=" * 70)

    # Parse the markdown files
    parsed_data = parse_podcast_data(podcast_files)
    print(f"\nParsed {len(parsed_data)} podcast documents")

    # Chunk by paragraphs with size=30, overlap=15
    chunks = chunk_documents_by_paragraphs(
        parsed_data,
        size=30,
        step=15
    )

    print(f"\nNumber of chunks created: {len(chunks)}")

    # Show example chunk info
    if chunks:
        print(f"\nExample chunk:")
        print(f"  Filename: {chunks[0].get('filename', 'N/A')}")
        print(f"  Start position: {chunks[0]['start']}")
        print(f"  Content preview: {chunks[0]['content'][:200]}...")

    print("\n" + "=" * 70)
    print("Question 6: Searching with minsearch...")
    print("=" * 70)

    # Search for the query
    query = "how do I make money with AI?"
    print(f"\nQuery: '{query}'")

    results = search_podcasts(chunks, query, num_results=5)

    print(f"\nFound {len(results)} results")

    if results:
        first_result = results[0]
        first_episode = first_result.get('filename', 'N/A')

        print(f"\nFirst episode in results: {first_episode}")
        print(f"\nTop 3 results:")
        for i, result in enumerate(results[:3], 1):
            episode = result.get('filename', 'N/A')
            content_preview = result.get('content', '')[:150]
            print(f"\n{i}. Episode: {episode}")
            print(f"   Preview: {content_preview}...")
