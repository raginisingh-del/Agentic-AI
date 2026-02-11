"""
RAG Pipeline Module for Research Paper Question Answering
Author: RAG Student
Date: 2026
Purpose: Core RAG functions including PDF extraction, chunking, embedding, retrieval, and generation
"""

import PyPDF2
from typing import List, Tuple, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class RAGPipeline:
    """
    Complete RAG Pipeline for Research Paper Question Answering
    
    Components:
    1. Text Extraction: PDF → Raw Text
    2. Chunking: Raw Text → Chunks (with overlap)
    3. Embedding: Chunks → Vector Embeddings
    4. Storage: Embeddings → FAISS Index
    5. Retrieval: Query → Top-K Similar Chunks
    6. Generation: Context + Query → Answer
    """
    
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize RAG Pipeline with embedding model.
        
        Args:
            embedding_model_name: Name of the sentence-transformer model to use
        """
        print(f"Initializing RAG Pipeline...")
        print(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Storage for chunks and embeddings
        self.chunks = []
        self.embeddings = None
        self.faiss_index = None
        
        print(f"✓ Embedding model loaded (dimension: {self.embedding_dim})")
    
    # ==================== STEP 1: TEXT EXTRACTION ====================
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Extracted text as string
        """
        print(f"\n[STEP 1] Extracting text from PDF: {pdf_path}")
        
        extracted_text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    extracted_text += page.extract_text() + "\n"
            
            print(f"✓ Extracted text from {num_pages} pages")
            print(f"✓ Total characters: {len(extracted_text)}")
            return extracted_text
        
        except Exception as e:
            print(f"✗ Error extracting PDF: {str(e)}")
            raise
    
    # ==================== STEP 2: TEXT CHUNKING ====================
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            chunk_size: Number of characters per chunk
            overlap: Number of overlapping characters between chunks
        
        Returns:
            List of text chunks with overlap
        """
        print(f"\n[STEP 2] Chunking text (chunk_size={chunk_size}, overlap={overlap})")
        
        chunks = []
        step = chunk_size - overlap  # Step size for non-overlapping portion
        
        # Split into words first for better semantic boundaries
        words = text.split()
        char_count = 0
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            char_count += len(word) + 1  # +1 for space
            
            if char_count >= chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                
                # Create overlap by going back
                overlap_words = []
                word_count = 0
                for w in reversed(current_chunk):
                    overlap_words.insert(0, w)
                    word_count += len(w) + 1
                    if word_count >= overlap:
                        break
                
                current_chunk = overlap_words
                char_count = sum(len(w) + 1 for w in current_chunk)
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        self.chunks = chunks
        
        print(f"✓ Created {len(chunks)} chunks")
        print(f"  - Average chunk size: {np.mean([len(c) for c in chunks]):.0f} characters")
        print(f"  - Min chunk size: {min(len(c) for c in chunks)} characters")
        print(f"  - Max chunk size: {max(len(c) for c in chunks)} characters")
        
        return chunks
    
    # ==================== STEP 3: EMBEDDING GENERATION ====================
    
    def generate_embeddings(self, chunks: List[str] = None, batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for all chunks.
        
        Args:
            chunks: List of text chunks (uses self.chunks if None)
            batch_size: Batch size for embedding generation
        
        Returns:
            numpy array of embeddings (shape: num_chunks x embedding_dim)
        """
        print(f"\n[STEP 3] Generating embeddings for {len(self.chunks)} chunks")
        
        if chunks is not None:
            self.chunks = chunks
        
        embeddings = self.embedding_model.encode(
            self.chunks,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        self.embeddings = embeddings
        
        print(f"✓ Generated embeddings")
        print(f"  - Shape: {embeddings.shape}")
        print(f"  - Dtype: {embeddings.dtype}")
        
        return embeddings
    
    # ==================== STEP 4: FAISS INDEXING ====================
    
    def create_faiss_index(self, embeddings: np.ndarray = None) -> faiss.IndexFlatL2:
        """
        Create FAISS index for similarity search.
        
        Args:
            embeddings: Embeddings to index (uses self.embeddings if None)
        
        Returns:
            FAISS index object
        """
        print(f"\n[STEP 4] Creating FAISS index")
        
        if embeddings is not None:
            self.embeddings = embeddings
        
        # Use L2 distance metric (Euclidean distance)
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        self.faiss_index.add(self.embeddings.astype(np.float32))
        
        print(f"✓ FAISS index created")
        print(f"  - Index type: IndexFlatL2 (L2 distance)")
        print(f"  - Indexed vectors: {self.faiss_index.ntotal}")
        
        return self.faiss_index
    
    # ==================== STEP 5: RETRIEVAL ====================
    
    def retrieve_top_chunks(
        self, 
        query: str, 
        top_k: int = 3
    ) -> Tuple[List[str], List[float]]:
        """
        Retrieve top-K relevant chunks for a query.
        
        Args:
            query: Query string
            top_k: Number of top chunks to retrieve
        
        Returns:
            Tuple of (chunks, similarity_scores)
        """
        print(f"\n[STEP 5] Retrieving top-{top_k} relevant chunks")
        print(f"Query: {query}")
        
        # Encode query
        query_embedding = self.embedding_model.encode(
            query, 
            convert_to_numpy=True
        ).reshape(1, -1)
        
        # Search in FAISS index
        distances, indices = self.faiss_index.search(
            query_embedding.astype(np.float32), 
            k=top_k
        )
        
        # Convert distances to similarity scores (inverse of L2 distance)
        # L2 distance ranges from 0 to infinity, so we use 1/(1+distance)
        scores = 1 / (1 + distances[0])
        
        # Retrieve corresponding chunks
        retrieved_chunks = [self.chunks[idx] for idx in indices[0]]
        
        print(f"✓ Retrieved {len(retrieved_chunks)} chunks")
        for i, (chunk, score) in enumerate(zip(retrieved_chunks, scores), 1):
            print(f"  [{i}] Similarity: {score:.4f} | Length: {len(chunk)} chars")
        
        return retrieved_chunks, scores.tolist()
    
    # ==================== STEP 6: ANSWER GENERATION ====================
    
    def format_context_for_generation(
        self, 
        chunks: List[str], 
        max_length: int = 2000
    ) -> str:
        """
        Format retrieved chunks into context for the generator.
        
        Args:
            chunks: List of retrieved chunks
            max_length: Maximum context length in characters
        
        Returns:
            Formatted context string
        """
        context = ""
        for i, chunk in enumerate(chunks, 1):
            if len(context) + len(chunk) <= max_length:
                context += f"\n[Source {i}]\n{chunk}\n"
            else:
                break
        
        return context if context else chunks[0]
    
    def generate_answer(
        self, 
        query: str, 
        context: str, 
        max_length: int = 200
    ) -> str:
        """
        Generate answer based on query and context.
        
        For demonstration, this creates a structured response.
        In production, use transformer-based summarization models.
        
        Args:
            query: Original query
            context: Retrieved context
            max_length: Maximum answer length
        
        Returns:
            Generated answer string
        """
        print(f"\n[STEP 6] Generating answer")
        
        # Simple extractive-based answer generation
        # (In production, use fine-tuned models like FLAN-T5, Mistral, etc.)
        
        sentences = context.split('.')
        answer = ". ".join([s.strip() for s in sentences[:2] if s.strip()])
        
        if len(answer) > max_length:
            answer = answer[:max_length] + "..."
        
        return answer
    
    # ==================== COMPLETE PIPELINE ====================
    
    def run_pipeline(
        self, 
        pdf_path: str, 
        query: str,
        chunk_size: int = 500,
        overlap: int = 100,
        top_k: int = 3
    ) -> Dict:
        """
        Run complete RAG pipeline from PDF to answer.
        
        Args:
            pdf_path: Path to PDF file
            query: User query
            chunk_size: Chunk size for splitting
            overlap: Overlap between chunks
            top_k: Number of top chunks to retrieve
        
        Returns:
            Dictionary containing results
        """
        print("\n" + "="*70)
        print("RAG PIPELINE EXECUTION")
        print("="*70)
        
        # Step 1: Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Step 2: Chunk text
        chunks = self.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        # Step 3: Generate embeddings
        embeddings = self.generate_embeddings()
        
        # Step 4: Create FAISS index
        self.create_faiss_index()
        
        # Step 5: Retrieve chunks
        retrieved_chunks, scores = self.retrieve_top_chunks(query, top_k=top_k)
        
        # Step 6: Generate answer
        context = self.format_context_for_generation(retrieved_chunks)
        answer = self.generate_answer(query, context)
        
        results = {
            "query": query,
            "retrieved_chunks": retrieved_chunks,
            "similarity_scores": scores,
            "formatted_context": context,
            "generated_answer": answer,
            "metadata": {
                "total_chunks": len(self.chunks),
                "chunk_size": chunk_size,
                "overlap": overlap,
                "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
                "top_k_retrieved": top_k
            }
        }
        
        return results
