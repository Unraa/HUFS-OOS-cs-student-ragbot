import glob
import os
import re
from typing import Dict, List, Tuple

import nbformat

from app.core.config import settings


def extract_markdown_from_notebook(notebook_path: str) -> str:
    """
    주피터 노트북(.ipynb)에서 마크다운 셀만 추출하여 하나의 문자열로 반환

    Args:
        notebook_path (str): 노트북 파일 경로

    Returns:
        str: 추출된 마크다운 내용
    """
    notebook = nbformat.read(notebook_path, as_version=4)
    markdown_cells = [
        cell["source"] for cell in notebook.cells if cell["cell_type"] == "markdown"
    ]
    return "\n\n".join(markdown_cells)


def read_markdown_file(file_path: str) -> str:
    """
    마크다운 파일(.md, .markdown)의 내용을 읽어 반환합니다.

    Args:
        file_path (str): 마크다운 파일 경로

    Returns:
        str: 마크다운 파일 내용
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def combine_markdown_documents(directory_path: str) -> str:
    """
    지정된 디렉토리에서 모든 노트북 파일과 마크다운 파일을 찾아 내용을 추출하고 합침

    Args:
        directory_path (str): 파일들이 있는 디렉토리 경로

    Returns:
        str: 합쳐진 마크다운 내용
    """
    # 노트북 파일과 마크다운 파일 목록 가져오기
    notebook_files = glob.glob(os.path.join(directory_path, "*.ipynb"))
    markdown_files = glob.glob(os.path.join(directory_path, "*.md")) + glob.glob(
        os.path.join(directory_path, "*.markdown")
    )

    combined_markdown = ""

    # 노트북 파일 처리
    for notebook_file in notebook_files:
        print(f"Processing notebook: {notebook_file}")
        markdown_content = extract_markdown_from_notebook(notebook_file)

        # 각 문서 사이에 구분자 추가
        if combined_markdown:
            combined_markdown += f"\n\n# 문서: {os.path.basename(notebook_file)}\n\n"
        else:
            combined_markdown += f"# 문서: {os.path.basename(notebook_file)}\n\n"

        combined_markdown += markdown_content

    # 마크다운 파일 처리
    for markdown_file in markdown_files:
        print(f"Processing markdown: {markdown_file}")
        markdown_content = read_markdown_file(markdown_file)

        # 각 문서 사이에 구분자 추가
        if combined_markdown:
            combined_markdown += f"\n\n# 문서: {os.path.basename(markdown_file)}\n\n"
        else:
            combined_markdown += f"# 문서: {os.path.basename(markdown_file)}\n\n"

        combined_markdown += markdown_content

    return combined_markdown


def chunk_by_heading(
    markdown_text: str, heading_level: str = "##"
) -> List[Dict[str, str]]:
    """
    마크다운 텍스트를 지정된 헤딩 레벨('##')을 기준으로 청킹

    Args:
        markdown_text (str): 마크다운 텍스트
        heading_level (str, optional): 청킹 기준이 되는 헤딩 레벨. 기본값은 '##'.

    Returns:
        List[Dict[str, str]]: 청킹된 내용의 리스트. 각 항목은 {'title': 제목, 'content': 내용} 형태의 딕셔너리.
    """
    # 헤딩 레벨에 맞는 정규식 패턴 생성
    pattern = f"^{heading_level} .*$"

    # 헤딩으로 시작하는 라인 찾기
    lines = markdown_text.split("\n")
    chunk_starts = []

    for i, line in enumerate(lines):
        if re.match(pattern, line):
            chunk_starts.append(i)

    # 청크가 없는 경우 처리
    if not chunk_starts:
        print(f"경고: '{heading_level}'로 시작하는 헤딩을 찾을 수 없습니다.")
        return []

    # 청크 생성
    chunks = []

    for i, start_idx in enumerate(chunk_starts):
        # 청크의 제목 (헤딩 라인)
        title = lines[start_idx].replace(heading_level + " ", "")

        # 청크의 내용
        if i < len(chunk_starts) - 1:
            content = "\n".join(lines[start_idx : chunk_starts[i + 1]])
        else:
            content = "\n".join(lines[start_idx:])

        chunks.append({"title": title, "content": content, "source": f"chunk_{i+1}"})

    return chunks


def process_markdown_documents(
    directory_path: str = None, output_file: str = None
) -> Tuple[str, List[Dict[str, str]]]:
    """
    마크다운 문서를 처리하는 전체 파이프라인:
    1. 문서 수집 및 결합
    2. 헤딩 기준으로 청킹
    3. 파일로 저장

    Args:
        directory_path (str, optional): 노트북 파일들이 있는 디렉토리 경로
        output_file (str, optional): 결합된 마크다운을 저장할 파일 경로.

    Returns:
        Tuple[str, List[Dict[str, str]]]: 결합된 마크다운 텍스트와 청킹된 내용 리스트
    """
    if directory_path is None:
        directory_path = os.path.join(settings.DOCS_DIR, "raw")

    if output_file is None:
        output_file = os.path.join(settings.DOCS_DIR, "combined_markdown.md")

    # 출력 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 1. 마크다운 문서 결합
    combined_markdown = combine_markdown_documents(directory_path)

    # 2. 결합된 마크다운 저장
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_markdown)

    print(f"합쳐진 마크다운 저장 완료: {output_file}")

    # 3. 헤딩 기준으로 청킹
    chunks = chunk_by_heading(combined_markdown)

    print(f"총 {len(chunks)}개의 청크로 분할됨")

    return combined_markdown, chunks
