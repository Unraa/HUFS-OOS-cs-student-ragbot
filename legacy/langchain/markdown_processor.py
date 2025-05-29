import os
from typing import Dict, List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document

from app.core.config import settings


class NotebookLoader(TextLoader):
    """주피터 노트북 파일을 로드하는 커스텀 로더"""

    def load(self) -> List[Document]:
        import nbformat

        notebook = nbformat.read(self.file_path, as_version=4)
        markdown_cells = [
            cell["source"] for cell in notebook.cells if cell["cell_type"] == "markdown"
        ]
        content = "\n\n".join(markdown_cells)

        metadata = {"source": self.file_path}
        return [Document(page_content=content, metadata=metadata)]


def load_documents(directory_path: str = None) -> List[Document]:
    """
    지정된 디렉토리에서 마크다운 파일과 노트북 파일을 로드합니다.

    Args:
        directory_path (str): 문서가 있는 디렉토리 경로

    Returns:
        List[Document]: 로드된 문서 리스트
    """
    if directory_path is None:
        directory_path = os.path.join(settings.DOCS_DIR, "raw")

    documents = []

    try:
        # 마크다운 파일 로드
        md_loader = DirectoryLoader(
            directory_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        md_docs = md_loader.load()
        documents.extend(md_docs)
        print(f"마크다운 파일 {len(md_docs)}개 로드됨")
    except Exception as e:
        print(f"마크다운 파일 로드 중 오류: {str(e)}")

    try:
        # 노트북 파일 로드
        notebook_loader = DirectoryLoader(
            directory_path,
            glob="**/*.ipynb",
            loader_cls=NotebookLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        notebook_docs = notebook_loader.load()
        documents.extend(notebook_docs)
        print(f"노트북 파일 {len(notebook_docs)}개 로드됨")
    except Exception as e:
        print(f"노트북 파일 로드 중 오류: {str(e)}")

    print(f"총 {len(documents)}개의 문서를 로드했습니다.")
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    문서를 청크로 분할합니다.

    Args:
        documents (List[Document]): 분할할 문서 리스트

    Returns:
        List[Document]: 분할된 청크 리스트
    """
    # 빈 문서나 너무 짧은 문서 필터링
    filtered_documents = []
    for doc in documents:
        if doc.page_content and len(doc.page_content.strip()) > 50:  # 최소 50자 이상
            filtered_documents.append(doc)
        else:
            print(f"너무 짧은 문서 제외: {doc.metadata.get('source', 'unknown')}")

    if not filtered_documents:
        print("유효한 문서가 없습니다.")
        return []

    print(f"필터링 후 {len(filtered_documents)}개 문서가 남았습니다.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(filtered_documents)

    # 빈 청크 제거
    valid_chunks = [chunk for chunk in chunks if chunk.page_content.strip()]

    print(f"문서를 {len(valid_chunks)}개의 유효한 청크로 분할했습니다.")

    return valid_chunks


def process_markdown_documents(
    directory_path: str = None,
) -> Tuple[List[Document], List[Document]]:
    """
    마크다운 문서를 처리하는 전체 파이프라인:
    1. 문서 로드
    2. 청크로 분할

    Args:
        directory_path (str): 문서가 있는 디렉토리 경로

    Returns:
        Tuple[List[Document], List[Document]]: (원본 문서, 분할된 청크)
    """
    # 1. 문서 로드
    documents = load_documents(directory_path)

    if not documents:
        print("로드된 문서가 없습니다.")
        return [], []

    # 2. 문서 분할
    chunks = split_documents(documents)

    return documents, chunks


# 기존 함수들과의 호환성을 위한 래퍼 함수들
def extract_markdown_from_notebook(notebook_path: str) -> str:
    """기존 코드와의 호환성을 위한 래퍼 함수"""
    import nbformat

    notebook = nbformat.read(notebook_path, as_version=4)
    markdown_cells = [
        cell["source"] for cell in notebook.cells if cell["cell_type"] == "markdown"
    ]
    return "\n\n".join(markdown_cells)


def chunk_by_heading(
    markdown_text: str, heading_level: str = "##"
) -> List[Dict[str, str]]:
    """기존 코드와의 호환성을 위한 래퍼 함수"""
    import re

    pattern = f"^{heading_level} .*$"
    lines = markdown_text.split("\n")
    chunk_starts = []

    for i, line in enumerate(lines):
        if re.match(pattern, line):
            chunk_starts.append(i)

    if not chunk_starts:
        print(f"경고: '{heading_level}'로 시작하는 헤딩을 찾을 수 없습니다.")
        return []

    chunks = []
    for i, start_idx in enumerate(chunk_starts):
        title = lines[start_idx].replace(heading_level + " ", "")

        if i < len(chunk_starts) - 1:
            content = "\n".join(lines[start_idx : chunk_starts[i + 1]])
        else:
            content = "\n".join(lines[start_idx:])

        chunks.append({"title": title, "content": content, "source": f"chunk_{i+1}"})

    return chunks
