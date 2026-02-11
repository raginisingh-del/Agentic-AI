# Quick Start Guide: RAG Research Paper QA

Get the RAG system running in 5 minutes!

##  Super Quick Start (Copy & Paste)

### Windows
```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install PyPDF2 sentence-transformers faiss-cpu jupyter numpy pandas -q

# 3. Start Jupyter from notebook folder
cd notebook
jupyter notebook

# 4. Open RAG_Research_Paper_QA.ipynb and run all cells
```

### Mac/Linux
```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install PyPDF2 sentence-transformers faiss-cpu jupyter numpy pandas -q

# 3. Start Jupyter from notebook folder
cd notebook
jupyter notebook

# 4. Open RAG_Research_Paper_QA.ipynb and run all cells
```

---

##  What Happens When You Run the Notebook

```
Cell 1: Install packages
  └─ Downloads required Python libraries
  
Cell 2: Imports and setup
  └─ Loads libraries and sets up paths
  
Cell 3: Initialize RAG pipeline
  └─ Loads embedding model (takes ~30 seconds on first run)
  
Cell 4: Extract PDF text
  └─ Reads agentic_uncertainty.pdf
  └─ Outputs: Page count, character count
  
Cell 5: Chunk text
  └─ Splits into 500-char chunks with 100-char overlap
  └─ Outputs: Number of chunks, size statistics
  
Cell 6: Generate embeddings
  └─ Creates 384-dimensional vectors for each chunk
  └─ Outputs: Embedding shape and statistics
  
Cell 7: Create FAISS index
  └─ Builds search index for fast retrieval
  └─ Outputs: Index configuration
  
Cell 8-10: Test Query 1-3
  └─ Retrieves relevant chunks for each query
  └─ Generates answers
  └─ Shows similarity scores
  
Cell 11: Results summary
  └─ Displays table with retrieval metrics
```

**Total Runtime:** ~5-10 minutes on CPU (first run slower due to model download)

---

##  Understanding the Results

### Similarity Scores
```
Range: 0.0 to 1.0
  0.0 = No similarity
  0.5 = Moderate match
  1.0 = Perfect match

Good retrieval:
  Top-1 score > 0.7
  Average score > 0.6
```

### Example Output Format

```
=== TEST QUERY 1 ===
Query: What problem does the paper address?

Retrieved Context:
[Chunk 1] (Similarity: 0.8792)
  → "The paper addresses uncertainty estimation in..."
  
[Chunk 2] (Similarity: 0.7654)
  → "Existing methods fail to capture epistemic..."
  
[Chunk 3] (Similarity: 0.6821)
  → "We propose a Bayesian framework..."

Generated Answer:
The paper addresses the problem of uncertainty estimation...
```

---

##  Exploring the Code Structure

### Understand the Flow

```python
# Step-by-step in notebook:

# 1. Initialize
rag = RAGPipeline()

# 2. Extract text
text = rag.extract_text_from_pdf('data/agentic_uncertainty.pdf')

# 3. Create chunks
chunks = rag.chunk_text(text, chunk_size=500, overlap=100)

# 4. Generate embeddings
embeddings = rag.generate_embeddings(chunks)

# 5. Build index
faiss_index = rag.create_faiss_index(embeddings)

# 6. Query
chunks, scores = rag.retrieve_top_chunks("Your question?", top_k=3)

# 7. Answer
answer = rag.generate_answer("Your question?", context)
```

### Import Functions

```python
# From src/rag_pipeline.py
from rag_pipeline import RAGPipeline

# From src/utils.py
from utils import save_chunks, format_retrieved_context, calculate_metrics
```

---

##  Common Modifications

### Change Top-K Retrieved Chunks
```python
# Default is 3, get more:
chunks, scores = rag.retrieve_top_chunks(query, top_k=5)

# Get fewer:
chunks, scores = rag.retrieve_top_chunks(query, top_k=1)
```

### Adjust Chunk Size
```python
# Smaller chunks (more granular):
chunks = rag.chunk_text(text, chunk_size=250, overlap=50)

# Larger chunks (more context):
chunks = rag.chunk_text(text, chunk_size=1000, overlap=200)
```

### Use Different Embedding Model
```python
# More accurate but slower:
rag = RAGPipeline(
    embedding_model_name="sentence-transformers/all-mpnet-base-v2"
)

# Faster but less accurate:
rag = RAGPipeline(
    embedding_model_name="sentence-transformers/all-MiniLM-L12-v2"
)
```

---

##  Test Your Own Queries

After running the notebook, add a new cell:

```python
# Test your own query
my_query = "What is the main dataset used?"

retrieved_chunks, scores = rag.retrieve_top_chunks(my_query, top_k=3)

print(f"Query: {my_query}\n")
print("Retrieved Chunks:")
for i, (chunk, score) in enumerate(zip(retrieved_chunks, scores), 1):
    print(f"\n[{i}] Similarity: {score:.4f}")
    print(chunk[:200] + "...")

# Generate answer
context = rag.format_context_for_generation(retrieved_chunks)
answer = rag.generate_answer(my_query, context)
print(f"\nAnswer: {answer}")
```

---

##  Troubleshooting

### "Module not found: faiss"
```bash
pip install faiss-cpu --no-cache-dir
```

### Slow on first run (downloading model)
- This is normal! Model downloads ~45MB
- Takes ~1-2 minutes first time
- Cached after that

### "PDF not found" error
- Verify: `data/agentic_uncertainty.pdf` exists
- Check file path is correct
- Permission to read file

### Memory issues with large PDFs
```python
# Process in batches
embeddings = rag.generate_embeddings(chunks, batch_size=32)
```

---

##  Performance Expectations

### Hardware Impact

**CPU (Intel i7):**
- Model load: 30 seconds
- Embedding generation: 2-3 seconds per 2000 chunks
- Query retrieval: 10-20 ms
- Total for 3 queries: ~5-10 minutes

**GPU (NVIDIA):**
- Model load: 10 seconds
- Embedding generation: 0.5 seconds per 2000 chunks
- Query retrieval: 5-10 ms
- Total for 3 queries: ~2-3 minutes

### Scalability

| PDFs | Chunks | Recommendation |
|------|--------|---|
| 1-5 | <10K | FAISS (current) |
| 5-20 | 10-100K | FAISS with IVF |
| 20+ | 100K+ | Pinecone/Weaviate |

---

##  Learning Path

### Beginner
1. Run the notebook cell-by-cell
2. Read the markdown explanations
3. Understand the pipeline stages

### Intermediate
4. Modify chunk size and top_k
5. Try different queries
6. Examine retrieved chunks

### Advanced
7. Implement custom embedding model
8. Add metadata filtering
9. Build web UI with Gradio
10. Deploy to cloud

---

##  Next Steps

### Learn More
- Read `README.md` for detailed documentation
- Read `ASSIGNMENT_REPORT.md` for complete technical details
- Check comments in `src/rag_pipeline.py` for implementation details

### Build On It
- Add more PDFs to the index
- Implement better chunking strategies
- Add reranking with cross-encoders
- Build web interface (Streamlit/Gradio)

### Deploy It
- Docker containerization
- Cloud deployment (AWS/Azure/GCP)
- API endpoint creation
- Multi-user support

---

##  Success Criteria

✓ PDF text successfully extracted  
✓ Text chunks created with proper overlap  
✓ Embeddings generated for all chunks  
✓ FAISS index created and searchable  
✓ All 3 test queries return results with scores > 0.6  
✓ Generated answers are coherent and relevant  

If you see all ✓, your RAG system is working!

---

##  Tips & Tricks

1. **Save your progress:**
   ```python
   save_embeddings(embeddings, 'output/embeddings.pkl')
   save_chunks(chunks, 'output/chunks.txt')
   ```

2. **Inspect chunks:**
   ```python
   # Look at a specific chunk
   print(chunks[42])  # Print chunk 42
   print(len(chunks[42]))  # See its length
   ```

3. **Compare queries:**
   ```python
   queries = [
       "What are the methods?",
       "What is the methodology?",
       "How does it work?"
   ]
   # Similar queries should retrieve similar chunks
   ```

4. **Analyze embedding distribution:**
   ```python
   import numpy as np
   print(f"Mean: {embeddings.mean():.4f}")
   print(f"Std: {embeddings.std():.4f}")
   print(f"Min: {embeddings.min():.4f}")
   print(f"Max: {embeddings.max():.4f}")
   ```

---

##  FAQ

**Q: Can I use my own PDF?**  
A: Yes! Replace path in `extract_text_from_pdf()`. Works for any text-based PDF.

**Q: How do I make it faster?**  
A: Use GPU for embeddings, or try smaller embedding model (all-MiniLM-L12-v2).

**Q: Can I deploy this?**  
A: Yes! See ASSIGNMENT_REPORT.md section 4 for production guidelines.

**Q: How is this different from ChatGPT?**  
A: RAG grounds answers in your documents; ChatGPT uses general knowledge. RAG = more accurate for specific domains.

---

## 📞 Getting Help

1. Check error messages in terminal
2. Review README.md for detailed docs
3. Read ASSIGNMENT_REPORT.md for technical details
4. Check comments in src/*.py files
5. Review notebook explanations in markdown cells

---

**Good luck! You're building a real RAG system! 🚀**
