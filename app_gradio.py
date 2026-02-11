"""
Gradio Web UI for RAG Research Paper Question Answering System
Author: RAG Student
Date: 2026
Purpose: Simple web interface for interactive RAG queries
"""

import gradio as gr
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_pipeline import RAGPipeline
from utils import format_retrieved_context


class RAGWebUI:
    """Web UI for RAG Pipeline using Gradio"""
    
    def __init__(self, pdf_path: str, chunk_size: int = 500, overlap: int = 100):
        """Initialize RAG pipeline and build UI"""
        self.rag = RAGPipeline()
        
        # Initialize pipeline
        print("Initializing RAG system...")
        text = self.rag.extract_text_from_pdf(pdf_path)
        chunks = self.rag.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        embeddings = self.rag.generate_embeddings(chunks)
        self.rag.create_faiss_index(embeddings)
        
        print(f"✓ RAG system ready with {len(chunks)} chunks")
    
    def process_query(self, query: str, top_k: int) -> tuple:
        """Process user query and return results"""
        if not query.strip():
            return "Please enter a question", "", ""
        
        # Retrieve chunks
        chunks, scores = self.rag.retrieve_top_chunks(query, top_k=top_k)
        
        # Format retrieved context
        retrieved_text = format_retrieved_context(chunks, scores)
        
        # Generate answer
        context = self.rag.format_context_for_generation(chunks)
        answer = self.rag.generate_answer(query, context)
        
        # Format scores display
        scores_display = "\n".join([
            f"Chunk {i+1}: {score:.4f} similarity"
            for i, score in enumerate(scores)
        ])
        
        return answer, retrieved_text, scores_display
    
    def launch(self, share: bool = True):
        """Launch Gradio interface"""
        
        with gr.Blocks(title="RAG Research Paper QA") as interface:
            gr.Markdown("""
            # 📖 RAG Research Paper Question Answering
            
            Ask questions about the research paper. The system will:
            1. **Retrieve** the most relevant text chunks
            2. **Display** similarity scores
            3. **Generate** an answer based on the retrieved context
            """)
            
            with gr.Row():
                with gr.Column():
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="E.g., What problem does the paper address?",
                        lines=2
                    )
                    
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=3,
                        step=1,
                        label="Number of Chunks to Retrieve"
                    )
                    
                    submit_btn = gr.Button("🔍 Search", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    answer_output = gr.Textbox(
                        label="Generated Answer",
                        interactive=False,
                        lines=5
                    )
                
                with gr.Column():
                    scores_output = gr.Textbox(
                        label="Similarity Scores",
                        interactive=False,
                        lines=5
                    )
            
            retrieved_output = gr.Textbox(
                label="Retrieved Context (Full Chunks)",
                interactive=False,
                lines=10
            )
            
            # Connect submit button
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input, top_k_slider],
                outputs=[answer_output, retrieved_output, scores_output]
            )
            
            # Also submit on Enter key
            query_input.submit(
                fn=self.process_query,
                inputs=[query_input, top_k_slider],
                outputs=[answer_output, retrieved_output, scores_output]
            )
            
            gr.Markdown("""
            ## 📝 Example Queries
            
            - "What problem does the paper address?"
            - "What methodology is proposed?"
            - "What are the main contributions?"
            - "What datasets are used?"
            - "How does the approach compare to baselines?"
            
            ---
            
            **Technical Details:**
            - **Embedding Model:** Sentence-Transformers (all-MiniLM-L6-v2)
            - **Vector Database:** FAISS (L2 distance)
            - **Chunk Size:** 500 characters with 100 character overlap
            - **Retrieval:** Top-K nearest neighbors search
            """)
        
        # Launch
        interface.launch(share=share)


def main():
    """Main entry point"""
    pdf_path = Path(__file__).parent / "data" / "agentic_uncertainty.pdf"
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return
    
    # Create and launch UI
    ui = RAGWebUI(str(pdf_path))
    ui.launch(share=True)


if __name__ == "__main__":
    main()
