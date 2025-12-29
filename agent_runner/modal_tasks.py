
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
    image = (
        modal.Image.debian_slim()
        .pip_install(
            "networkx", 
            "scikit-learn", 
            "numpy",
            "torch",
            "transformers",
            "accelerate", 
            "pillow",
            "sentencepiece",
            "einops", 
            "transformers_stream_generator",
            "tiktoken"
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

    # 3. PDF Ingestion (CPU Pypdf + Optional GPU Vision in future)
    @app.function(image=image.pip_install("pypdf"), timeout=600)
    def cloud_process_pdf(file_bytes: bytes, filename: str):
        """
        Ingests a PDF in the cloud via pypdf.
        """
        import io
        import pypdf
        
        stream = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(stream)
        
        full_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"## Page {i+1}\n{text}")
            
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
        
        model_id = "Qwen/Qwen2-VL-72B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        img1 = Image.open(io.BytesIO(reference_bytes))
        img2 = Image.open(io.BytesIO(candidate_bytes))

        prompt = "Compare Image 1 (Ref) and Image 2 (Candidate). Identify broken parts, rust, or defects."
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img1},
                    {"type": "image", "image": img2},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[img1, img2], padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids = [output_ids[len(inputs.input_ids):] for inputs, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return {"detected_changes": [output_text], "severity": "UNKNOWN", "confidence": 0.95}

    @app.local_entrypoint()
    def test_main():
        print("🚀 [1/3] Testing Cloud Graph Detection...")
        nodes = [1, 2, 3, 4, 5]
        edges = [(1,2), (2,3), (3,1), (4,5)]
        res_graph = graph_community_detection.remote(nodes, edges)
        print(f"✅ Graph Result: {res_graph}")

        print("\n🚀 [2/3] Testing Unified 72B Model (Reasoning)...")
        res_reason = cloud_heavy_reasoning.remote("Antigravity is a project.", "What is Antigravity?")
        print(f"✅ Reasoning Result: {res_reason}")

        print("\n🚀 [3/3] Testing PDF Ingestion (CPU Pypdf)...")
        # Create dummy PDF bytes
        import io
        from pypdf import PdfWriter
        buf = io.BytesIO()
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
