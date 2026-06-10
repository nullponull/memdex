"""
Tests for utility functions
"""

import pytest
import tempfile
import os

from memdex.utils import (
    chunk_text,
    save_index, load_index
)



def test_chunk_text():
    """Test text chunking"""
    text = "This is a test. " * 50  # 800 characters
    
    # Test basic chunking
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)  # Allow for sentence boundaries
    
    # Test overlap
    for i in range(len(chunks) - 1):
        # Check that there's some overlap
        assert any(word in chunks[i+1] for word in chunks[i].split()[-5:])


def test_save_load_index():
    """Test index save and load"""
    test_data = {
        "metadata": [{"id": 1, "text": "test"}],
        "config": {"test": True}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Save
        save_index(test_data, temp_file)
        assert os.path.exists(temp_file)
        
        # Load
        loaded_data = load_index(temp_file)
        assert loaded_data == test_data
    finally:
        os.unlink(temp_file)