import io
import json
from typing import List, Dict, Any
import tiktoken
from pypdf import PdfReader
from app.core.config import settings

def get_tokenizer():
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None

tokenizer = get_tokenizer()

def count_tokens(text: str) -> int:
    if tokenizer:
        return len(tokenizer.encode(text))
    # Fallback approximation: 1 token ~ 4 characters
    return len(text) // 4

def split_text_into_chunks(
    text: str,
    metadata_template: Dict[str, Any],
    chunk_size: int = settings.CHUNK_SIZE_TOKENS,
    chunk_overlap: int = settings.CHUNK_OVERLAP_TOKENS
) -> List[Dict[str, Any]]:
    """
    Splits text using token boundaries (800 tokens max with 120 tokens overlap).
    """
    chunks: List[Dict[str, Any]] = []
    
    if tokenizer:
        tokens = tokenizer.encode(text)
        total_tokens = len(tokens)
        
        if total_tokens <= chunk_size:
            chunk_text = text.strip()
            if chunk_text:
                meta = metadata_template.copy()
                meta["chunk_index"] = 0
                meta["token_count"] = total_tokens
                chunks.append({"content": chunk_text, "metadata": meta})
            return chunks

        start_idx = 0
        chunk_idx = 0
        step = chunk_size - chunk_overlap
        
        while start_idx < total_tokens:
            end_idx = min(start_idx + chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_str = tokenizer.decode(chunk_tokens).strip()
            
            if chunk_str:
                meta = metadata_template.copy()
                meta["chunk_index"] = chunk_idx
                meta["token_count"] = len(chunk_tokens)
                chunks.append({"content": chunk_str, "metadata": meta})
                chunk_idx += 1
            
            if end_idx >= total_tokens:
                break
            start_idx += step
    else:
        # Fallback character-based sliding window if tiktoken unavailable
        step = (chunk_size - chunk_overlap) * 4
        window = chunk_size * 4
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = min(start + window, len(text))
            chunk_str = text[start:end].strip()
            if chunk_str:
                meta = metadata_template.copy()
                meta["chunk_index"] = chunk_idx
                meta["token_count"] = len(chunk_str) // 4
                chunks.append({"content": chunk_str, "metadata": meta})
                chunk_idx += 1
            if end >= len(text):
                break
            start += step

    return chunks

def parse_txt(file_bytes: bytes, filename: str, title: str) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8", errors="replace")
    metadata = {
        "filename": filename,
        "title": title,
        "file_type": "TXT"
    }
    return split_text_into_chunks(text, metadata)

def parse_json(file_bytes: bytes, filename: str, title: str) -> List[Dict[str, Any]]:
    raw_str = file_bytes.decode("utf-8", errors="replace")
    data = json.loads(raw_str)
    
    # Format JSON hierarchically into readable sections for high semantic retrieval
    formatted_sections = []
    if isinstance(data, dict):
        for k, v in data.items():
            section_title = k.replace("_", " ").title()
            if isinstance(v, list):
                items_str = "\n".join([f"- {json.dumps(item, ensure_ascii=False)}" if isinstance(item, dict) else f"- {item}" for item in v])
                formatted_sections.append(f"### {section_title} Rules & Data:\n{items_str}")
            elif isinstance(v, dict):
                formatted_sections.append(f"### {section_title} Rules & Data:\n{json.dumps(v, indent=2)}")
            else:
                formatted_sections.append(f"{section_title}: {v}")
    else:
        formatted_sections.append(json.dumps(data, indent=2))
        
    full_text = f"BANKING KNOWLEDGE BASE: {title}\n" + "\n\n".join(formatted_sections)
    metadata = {
        "filename": filename,
        "title": title,
        "file_type": "JSON"
    }
    return split_text_into_chunks(full_text, metadata)

def parse_pdf(file_bytes: bytes, filename: str, title: str) -> List[Dict[str, Any]]:
    reader = PdfReader(io.BytesIO(file_bytes))
    all_chunks: List[Dict[str, Any]] = []
    
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            metadata = {
                "filename": filename,
                "title": title,
                "file_type": "PDF",
                "page_number": page_num
            }
            chunks = split_text_into_chunks(page_text, metadata)
            all_chunks.extend(chunks)
            
    return all_chunks

def parse_document_content(file_bytes: bytes, filename: str, title: str) -> List[Dict[str, Any]]:
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return parse_pdf(file_bytes, filename, title)
    elif ext == "json":
        return parse_json(file_bytes, filename, title)
    else:
        return parse_txt(file_bytes, filename, title)
