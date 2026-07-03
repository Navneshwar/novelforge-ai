import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

def count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(re.findall(r'\w+', text))

def extract_name_from_text(text: str) -> List[str]:
    """Extract capitalized names from text"""
    if not text:
        return []
    
    pattern = r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b'
    matches = re.findall(pattern, text)
    
    # Remove common words that aren't names
    skip_words = {'The', 'A', 'An', 'And', 'Or', 'But', 'For', 'Nor', 'Yet', 'So', 'As', 'At', 'By', 'For', 'From', 'In', 'Of', 'On', 'To', 'With'}
    
    return [m for m in matches if m not in skip_words]

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common punctuation issues
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    return text.strip()

def parse_chapter_title(title: str) -> Dict[str, Any]:
    """Parse chapter title for metadata"""
    result = {
        "number": None,
        "title": title,
        "has_number": False
    }
    
    # Try to extract chapter number
    match = re.search(r'chapter\s+(\d+|[ivxlcdm]+)', title, re.IGNORECASE)
    if match:
        result["has_number"] = True
        try:
            number = match.group(1)
            if number.isdigit():
                result["number"] = int(number)
            else:
                # Roman numeral
                roman_map = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
                try:
                    result["number"] = roman_to_int(number.lower())
                except:
                    result["number"] = None
        except:
            result["number"] = None
    
    return result

def roman_to_int(roman: str) -> int:
    """Convert roman numeral to integer"""
    roman_map = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
    total = 0
    prev = 0
    for char in reversed(roman):
        current = roman_map.get(char, 0)
        if current < prev:
            total -= current
        else:
            total += current
        prev = current
    return total

def format_timestamp(dt: Optional[datetime]) -> str:
    """Format datetime for display"""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].strip() + suffix

def safe_json_loads(json_str: str) -> Dict:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except:
        return {}

def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """Safely convert to JSON string"""
    try:
        return json.dumps(data, indent=indent, default=str)
    except:
        return "{}"

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    path = Path(filename)
    return path.suffix.lower()

def is_valid_filename(filename: str) -> bool:
    """Check if filename is valid"""
    # Check for forbidden characters
    forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in forbidden:
        if char in filename:
            return False
    return True

def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    import re
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    slug = slug.strip('-')
    return slug or "untitled"

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

def detect_duplicates(items: List[str]) -> Dict[str, List[int]]:
    """Detect duplicate strings in a list"""
    seen = {}
    duplicates = {}
    
    for i, item in enumerate(items):
        key = item.lower().strip()
        if key in seen:
            if key not in duplicates:
                duplicates[key] = [seen[key]]
            duplicates[key].append(i)
        else:
            seen[key] = i
    
    return duplicates