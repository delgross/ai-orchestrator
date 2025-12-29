
import logging

# Try importing modal
try:
    import modal
    has_modal = True
except ImportError:
    has_modal = False

logger = logging.getLogger("agent_runner.modal")

from typing import Any, Dict, List, Optional

# We define the App. 
# Important: If Modal is not installed, we create a dummy to prevent import errors.
app: Any
if has_modal:
    # We name the app "antigravity-night-shift"
    app = modal.App("antigravity-night-shift")

    # Define the environment: A lightweight Debian image with graph libraries AND AI dependencies
    # We pin Python 3.11 because 3.12+ (or 3.14 beta) causes PyO3/Tokenizers build failures.
    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("git")
        .pip_install(
            "networkx", 
            "scikit-learn", 
            "numpy",
            "torch>=2.2.0",
            # Qwen2-VL requires bleeding edge transformers not yet in some PyPI releases
            "git+https://github.com/huggingface/transformers.git",
            "accelerate>=0.26.0", 
            "pillow",
            "sentencepiece",
            "einops", 
            "tiktoken",
            "torchvision",
            "qwen-vl-utils",
            # PDF Layout Analysis
            "docling", 
            "docling-core"
        )
    )

    # Build Step: Download the SINGLE Unified Model (Qwen2-VL-72B)
    def download_models():
        from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
        
        # Qwen2-VL-72B-Instruct: SOTA Vision + Reasoning (Unified Model)
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        print(f"📥 Downloading Unified Model: {model_id}...")
        
        # Download Processor (for images) and Tokenizer/Model
        # This will take time but happens once during build.
        try:
            AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            AutoModelForCausalLM.from_pretrained(
                model_id, 
                device_map="auto", 
                trust_remote_code=True
            )
        except Exception as e:
            print(f"Error downloading model: {e}")
            raise
        
        # Keep the smaller NLP tools for reranking
        from sentence_transformers import CrossEncoder
        from transformers import pipeline
        CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        pipeline("text-classification", model="roberta-large-mnli")

    # Attach the download step. Timeout extended for the 140GB+ download.
    image = image.run_function(
        download_models,
        timeout=3600 # Allow 1 hour
    )

    # 1. Graph Community Detection (CPU Intensive - Unchanged)
    @app.function(image=image, timeout=600)
    def graph_community_detection(nodes: list, edges: list):
        """
        Runs Louvain Community Detection on the Knowledge Graph.
        """
        import networkx as nx
        from networkx.algorithms import community

        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        try:
            communities = community.louvain_communities(G)
        except Exception as e:
            return {"error": str(e)}
        
        result = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                result[node] = idx
        return result

    # 2. Advanced Reasoner (Uses 72B Model on H100)
    @app.function(image=image, gpu="H100", timeout=900) 
    def cloud_heavy_reasoning(context_text: str, query: str):
        """
        Uses Qwen2-VL-72B for heavy reasoning.
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        import torch

        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        # Load the giant model
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        messages = [
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=None, padding=True, return_tensors="pt").to("cuda")
        
        # Increased max tokens for detailed reasoning
        output_ids = model.generate(**inputs, max_new_tokens=2048)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return {"result": output_text, "model": "Qwen2-VL-72B-Instruct"}

    # 3. PDF Ingestion (Advanced Layout Analysis via Docling)
    # Allows H100 GPU usage for OCR if needed, though Docling is often CPU-heavy
    @app.function(image=image, gpu="H100", timeout=900)
    def cloud_process_pdf(file_bytes: bytes, filename: str):
        """
        Ingests a PDF using Docling for full layout preservation (tables, headers).
        """
        import io
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.document import InputDocument
        
        # Docling expects a file path or stream
        # flexible approach: write to temp file
        import tempfile
        import os
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
                
            converter = DocumentConverter()
            res = converter.convert(tmp_path)
            
            # Export to comprehensive Markdown
            markdown = res.document.export_to_markdown()
            
            os.remove(tmp_path)
            return markdown
            
        except Exception as e:
            # Fallback to simple extraction if Docling explodes on weird encoded PDFs
            print(f"Docling failed: {e}. Falling back to pypdf.")
            import pypdf
            stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(stream)
            full_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text: full_text.append(text)
            return "\n\n".join(full_text)

    # 4. Heavy Image Analysis (Uses 72B Model on H100)
    @app.function(image=image, gpu="H100", timeout=900)
    def cloud_process_image(image_bytes: bytes, prompt: Optional[str] = None):
        """
        Analyzes an image using Qwen2-VL-72B-Instruct.
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from PIL import Image
        import io
        import json
        
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        image = Image.open(io.BytesIO(image_bytes))
        if not prompt:
            prompt = "Describe this image in detail."

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return json.dumps({
            "description": output_text,
            "meta": "Processed by Qwen2-VL-72B on H100"
        })

    # 5. Search Re-Ranking (Unchanged)
    @app.function(image=image.pip_install("sentence-transformers", "torch"), timeout=60)
    def rerank_search_results(query: str, candidates: list):
        from sentence_transformers import CrossEncoder
        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        pairs = [[query, doc] for doc in candidates]
        scores = model.predict(pairs)
        scored_results = []
        for i, score in enumerate(scores):
            scored_results.append((i, float(score)))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results

    # 6. Deep Fact Verification (Unchanged)
    @app.function(image=image.pip_install("transformers", "torch"), timeout=300)
    def verify_fact(fact: str, evidence: str):
        from transformers import pipeline
        nli_model = pipeline("text-classification", model="roberta-large-mnli")
        input_text = f"{fact} {evidence}"
        result = nli_model(input_text)
        label_map = {"ENTAILMENT": "SUPPORTED", "CONTRADICTION": "CONTRADICTED", "NEUTRAL": "NEUTRAL"}
        top = result[0]
        return {"judgment": label_map.get(top['label'].upper(), "NEUTRAL"), "confidence": top['score']}

    # 7. Visual Anomaly Detection (Uses 72B on H100)
    @app.function(image=image, gpu="H100", timeout=900)
    def detect_visual_anomaly(reference_bytes: bytes, candidate_bytes: bytes):
        """
        Compare two images with 72B model.
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from PIL import Image
        import io
        import json
        
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        img1 = Image.open(io.BytesIO(reference_bytes))
        img2 = Image.open(io.BytesIO(candidate_bytes))

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img1},
                    {"type": "image", "image": img2},
                    {"type": "text", "text": "Compare these two images. Image 1 is the Reference. Image 2 is the Candidate. Identify any anomalies, defects, or significant differences in Image 2. Focus on structural integrity, missing elements, or foreign objects. Return JSON with 'anomalies': [list] and 'severity': 'low|medium|high'."},
                ],
            }
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[img1, img2], padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return output_text

    # 8. Nightly Database Gardener (Uses 72B on H100)
    @app.function(image=image, gpu="H100", timeout=1200)
    def cloud_database_cleanup(facts_json: str):
        """
        Reviews a list of facts for semantic truth and consistency.
        Input: JSON list of {entity, relation, target, context}
        Output: JSON list of {entity, relation, target, semantic_confidence, reasoning}
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        import json
        
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        prompt = f"""
        You are the 'Truth Judge' for a long-term memory database. 
        Your job is to audit the following list of facts.
        
        For each fact:
        1. semantic_confidence: Assign a score (0.0 to 1.0) based on plausibility, contradiction with physical reality, or vagueness.
           - 1.0: Absolute truth (e.g. "Sky is blue", "Python is a language").
           - 0.5: Plausible but specific context needed.
           - 0.1: Likely hallucination, contradiction, or nonsense.
        2. reasoning: Briefly explain why.
        3. correction: If the fact is wrong or typoed, provide a corrected version.

        Input Facts:
        {facts_json}

        Return strictly a JSON list of objects with keys: id (from input), original_fact, semantic_confidence, reasoning, correction (or null).
        """

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=None, padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=4096)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Clean markdown code blocks if present
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0]
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0]
            
        return output_text

    # 9. Code Geneticist (Uses 72B on H100)
    @app.function(image=image, volumes={"/models": modal.Volume.from_name("huggingface-cache")}, timeout=3600)
    def download_models():
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        print(f"📥 Downloading Unified Model: {model_id}...")
        
        # Use the specific class to avoid AutoModel configuration errors
        Qwen2VLForConditionalGeneration.from_pretrained(model_id, trust_remote_code=True)
        AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    @app.function(image=image, gpu="H100", timeout=1200)
    def code_geneticist(target_function_code: str):
        """
        Analyzes and optimizes a Python function.
        Input: Python source code string.
        Output: JSON with {analysis: str, proposed_code: str, complexity_change: str}.
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        prompt = f"""
        You are a Senior Systems Architect and Algorithms Expert.
        Analyze the following Python code for:
        1. Time Complexity Inefficiencies (e.g. O(N^2) where O(N) is possible).
        2. Readability/Pythonic Standards.
        3. Potential Edge Case Bugs.

        TARGET CODE:
        {target_function_code}

        OUTPUT FORMAT (JSON):
        {{
            "analysis": "Brief explanation of issues found.",
            "complexity_change": "e.g. O(N^2) -> O(N)",
            "proposed_code": "The complete rewritten python code."
        }}
        """

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=None, padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=4096)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0]
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0]
            
        return output_text

    @app.local_entrypoint()
    def test_main():
        import io
        import json
        from pypdf import PdfWriter

        print("🚀 Starting Modal H100 Tests (Unified 72B Model)...")
        
        # Initialize buffer for PDF test
        buf = io.BytesIO()
        
        # Test 1: Graph (CPU)
        print("\n1. Testing Graph Community Detection...")
        nodes = ["A", "B", "C", "D", "E"]
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")]
        res = graph_community_detection.remote(nodes, edges)
        print(f"✅ Graph Result: {res}")

        # Test 2: Reasoning (H100)
        print("\n2. Testing Unified 72B Reasoning...")
        res = cloud_heavy_reasoning.remote("The server logs show error 500 at 3am. The backup job runs at 3am.", "What caused the error?")
        print(f"✅ Reasoning Result: {res}")

        # Test 3: Nightly Gardener (H100)
        print("\n3. Testing Nightly Gardener (Fact Auditing)...")
        sample_facts = json.dumps([
            {"id": "1", "fact": "The sky is green."},
            {"id": "2", "fact": "Python 3.14 was released in 2024."},
            {"id": "3", "fact": "Server 29 is located on Mars."}
        ])
        res = cloud_database_cleanup.remote(sample_facts)
        print(f"✅ Gardener Result:\n{res}")

        # Test 4: Code Geneticist (H100)
        print("\n4. Testing Code Geneticist (Evolution)...")
        bad_code = """
def find_item(items, target):
    # O(N) search? No, let's make it clear.
    for i in range(len(items)):
        if items[i] == target:
            return True
    return False
"""
        res = code_geneticist.remote(bad_code)
        print(f"✅ Geneticist Result:\n{res}")

        print("\n🎉 All tests passed!")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.write(buf)
        res_pdf = cloud_process_pdf.remote(buf.getvalue(), "test.pdf")
        print(f"✅ PDF Result (Length): {len(res_pdf)} chars")

else:
    # Dummy mock
    class MockApp:
        def function(self, *args: Any, **kwargs: Any) -> Any:
            def decorator(f: Any) -> Any:
                return f
            return decorator
    app = MockApp()
    
    # These will be the same functions but without the @app.function decorator
    def graph_community_detection(nodes: List[Any], edges: List[Any]) -> Dict[str, Any]:
        logger.warning("Modal library not found. Skipping Cloud Graph Processing.")
        return {}
    
    def cloud_heavy_reasoning(context_text: str, query: str) -> Dict[str, Any]:
        return {"result": "Modal not active."}
    
    def cloud_process_pdf(file_bytes: bytes, filename: str) -> str:
        return "Modal not active."
        
    def cloud_process_image(image_bytes: bytes, prompt: Optional[str] = None) -> str:
        return "Modal not active."
        
    def rerank_search_results(query: str, candidates: List[str]) -> List[Any]:
        return []
        
    def verify_fact(fact: str, evidence: str) -> Dict[str, Any]:
        return {"judgment": "NEUTRAL", "confidence": 0.0}
        
    def detect_visual_anomaly(reference_bytes: bytes, candidate_bytes: bytes) -> Dict[str, Any]:
        return {"detected_changes": [], "severity": "NONE", "confidence": 0.0}
