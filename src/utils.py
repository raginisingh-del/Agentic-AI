"""
Utility functions for RAG Research Paper Question Answering System
Author: RAG Student
Date: 2026
Purpose: Helper functions for text processing, chunking, and visualization
"""

import os
import pickle
from typing import List, Tuple
import numpy as np


def save_embeddings(embeddings: np.ndarray, filepath: str) -> None:
    """
    Save embeddings to disk for future use.
    
    Args:
        embeddings: numpy array of embeddings
        filepath: path to save the embeddings
    
    Returns:
        None
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(embeddings, f)
    print(f"✓ Embeddings saved to {filepath}")


def load_embeddings(filepath: str) -> np.ndarray:
    """
    Load embeddings from disk.
    
    Args:
        filepath: path to load embeddings from
    
    Returns:
        numpy array of embeddings
    """
    with open(filepath, 'rb') as f:
        embeddings = pickle.load(f)
    print(f"✓ Embeddings loaded from {filepath}")
    return embeddings


def save_chunks(chunks: List[str], filepath: str) -> None:
    """
    Save text chunks to disk.
    
    Args:
        chunks: list of text chunks
        filepath: path to save chunks
    
    Returns:
        None
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks):
            f.write(f"=== CHUNK {i+1} ===\n{chunk}\n\n")
    print(f"✓ Text chunks saved to {filepath}")


def calculate_overlap_tokens(chunk_size: int, overlap: int) -> int:
    """
    Calculate the number of tokens that will overlap between chunks.
    
    Args:
        chunk_size: Size of each chunk
        overlap: Overlap percentage (0-100)
    
    Returns:
        Number of overlapping tokens
    """
    return int(chunk_size * overlap / 100)


def print_system_info() -> None:
    """Print system configuration info for RAG system."""
    print("=" * 60)
    print("RAG SYSTEM CONFIGURATION")
    print("=" * 60)
    print(f"Python Version: {os.sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 60)


def format_retrieved_context(chunks: List[str], scores: List[float]) -> str:
    """
    Format retrieved chunks with their similarity scores.
    
    Args:
        chunks: list of retrieved text chunks
        scores: list of similarity scores
    
    Returns:
        Formatted string for display
    """
    result = "\n" + "="*70 + "\n"
    result += "RETRIEVED CONTEXT (Top Chunks)\n"
    result += "="*70 + "\n"
    
    for i, (chunk, score) in enumerate(zip(chunks, scores), 1):
        result += f"\n[Chunk {i}] (Similarity: {score:.4f})\n"
        result += "-" * 70 + "\n"
        result += chunk[:300] + "...\n" if len(chunk) > 300 else chunk + "\n"
    
    result += "\n" + "="*70 + "\n"
    return result


def calculate_metrics(num_chunks: int, chunk_size: int, overlap: int) -> dict:
    """
    Calculate and return metrics about the chunking strategy.
    
    Args:
        num_chunks: Total number of chunks
        chunk_size: Size of each chunk
        overlap: Overlap percentage
    
    Returns:
        Dictionary containing metrics
    """
    overlap_tokens = calculate_overlap_tokens(chunk_size, overlap)
    
    metrics = {
        "total_chunks": num_chunks,
        "chunk_size": chunk_size,
        "overlap_percentage": overlap,
        "overlap_tokens": overlap_tokens,
        "total_tokens_covered": num_chunks * (chunk_size - overlap_tokens)
    }
    
    return metrics
