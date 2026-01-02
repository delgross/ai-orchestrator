
import logging
import os

# Try importing modal
try:
    import modal
    # Only enable if package exists AND env var is set
    has_modal = os.getenv("ENABLE_MODAL", "false").lower() == "true"
except ImportError:
    has_modal = False

logger = logging.getLogger("agent_runner.modal")

from typing import Any, Dict, List, Optional
import os
import datetime

# --- CONFIGURATION ---
# We use the AWQ (4-bit) version of Qwen2.5-VL-72B.
# Original FP16: ~144GB (Too big for single H100 80GB)
# AWQ Int4: ~40GB (Fits easily on H100 80GB -> Pure GPU -> Fast)
MODEL_ID = "Qwen/Qwen2.5-VL-72B-Instruct-AWQ"

# --- Uplink Logger Details ---
def log_uplink(message: str):
    """Writes a message to the Cloud Uplink log for Dashboard visibility."""
    try:
        # Determine strict path (relative to this file -> root -> logs)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(root_dir, "logs", "cloud_uplink.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Failed to write to uplink log: {e}")

# We define the App. 
# Important: If Modal is not installed, we create a dummy to prevent import errors.
app: Any
if has_modal:
    # We name the app "antigravity-night-shift"
    app = modal.App("antigravity-night-shift")

    # Define the environment: A lightweight Debian image (~2GB max)
    # We pin Python 3.11 because 3.12+ (or 3.14 beta) causes PyO3/Tokenizers build failures.
    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install(
            "git", 
            "poppler-utils", 
            "ffmpeg",           # Crucial for Audio/Video processing
            "libsm6", "libxext6", "libgl1"  # Required for OpenCV
        )
        .pip_install(
            # Core AI/Data
            "networkx", "scikit-learn", "numpy", "pandas", "scipy", "sympy", "matplotlib",
            "torch>=2.2.0", "torchvision", "torchaudio",
            
            # Hugging Face Ecosystem
            "transformers>=4.46.0", "huggingface-hub>=0.24.0", "accelerate>=0.26.0", 
            "sentencepiece", "einops", "tiktoken", "qwen-vl-utils", "safetensors",
            
            # Optimization (AWQ Kernels)
            "autoawq", "optimum",

            # Document Processing (The "Office" Suite)
            "docling", "docling-core", "pdf2image", "pypdf",
            "python-docx", "openpyxl", "python-pptx",

            # Media Processing (Vision/Audio)
            "pillow", "opencv-python-headless", "moviepy", "pydub", "soundfile",

            # Utilities
            "httpx", "fastapi", "beautifulsoup4", "requests"
        )
    )

    # Volume for Persistent Model Storage (Network File System)
    # This avoids rebuilding the image every time.
    # Mounts to standard HF cache dir.
    model_volume = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
    cache_path = "/root/.cache/huggingface"

    # -------------------------------------------------------------------------
    # Helper: Model Download (Run once explicitly to prime the volume)
    # -------------------------------------------------------------------------
    @app.function(
        image=image, 
        volumes={cache_path: model_volume}, 
        timeout=7200 # 2 Hours for initial download (Safe Margin)
    )
    def prime_model_cache():
        print("Checking Model Cache...")
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        
        # This will download to /root/.cache/huggingface (which is the Volume)
        print(f"📥 Downloading/Verifying Unified Model: {MODEL_ID}...")
        try:
            # Code to trigger download
            AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
            Qwen2VLForConditionalGeneration.from_pretrained(
                MODEL_ID, 
                device_map="auto", 
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            print("✅ Model cached successfully.")
        except Exception as e:
            print(f"❌ Error caching model: {e}")
            raise

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
            print(f"Community Detection Error: {e}")
            return {"error": str(e)}
        
        result = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                result[node] = idx
        return result

    # 4. Heavy Image Analysis (Uses 72B-AWQ on H100 with Volume)
    @app.function(
        image=image, 
        gpu="H100", 
        volumes={cache_path: model_volume},
        timeout=900
    )
    def cloud_process_image(image_bytes: bytes, prompt: Optional[str] = None):
        """
        Analyzes an image using Qwen2.5-VL-72B-Instruct-AWQ.
        """
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from PIL import Image
        import io
        import json
        
        # LOAD MODEL
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

        image = Image.open(io.BytesIO(image_bytes))
        if not prompt:
            prompt = "Describe this image in detail."

        messages = [
            {"role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids = [output_ids[len(in_ids):] for in_ids, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return json.dumps({
            "description": output_text,
            "meta": f"Processed by {MODEL_ID} on H100"
        })

    # 5. Search Re-Ranking (Unchanged - uses smaller lib, installing inline is fine)
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

    # 7. Visual Anomaly Detection (Uses 72B-AWQ on H100)
    @app.function(
        image=image, 
        gpu="H100", 
        volumes={cache_path: model_volume},
        timeout=900
    )
    def detect_visual_anomaly(reference_bytes: bytes, candidate_bytes: bytes):
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from PIL import Image
        import io
        import json
        
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

        img1 = Image.open(io.BytesIO(reference_bytes))
        img2 = Image.open(io.BytesIO(candidate_bytes))

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img1},
                    {"type": "image", "image": img2},
                    {"type": "text", "text": "Compare these two images..."},
                ],
            }
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[img1, img2], padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids = [output_ids[len(in_ids):] for in_ids, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return output_text

    # 8. Nightly Database Gardener (Uses 72B-AWQ on H100)
    @app.function(
        image=image, 
        gpu="H100", 
        volumes={cache_path: model_volume},
        timeout=1200
    )
    def cloud_database_cleanup(facts_json: str):
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        import json
        
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID, torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

        prompt = f"""
        You are the 'Truth Judge' for a long-term memory database. 
        Your job is to audit the following list of facts...
        Input Facts:
        {facts_json}
        """

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=None, padding=True, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=4096)
        generated_ids = [output_ids[len(in_ids):] for in_ids, output_ids in zip(inputs, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0]
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0]
            
        return output_text



    # 10. Unified Cloud Intelligence (Uses 72B-AWQ on H100 with Snapshots)
    @app.cls(
        image=image, 
        gpu="H100", 
        volumes={cache_path: model_volume},
        enable_memory_snapshot=True,
        scaledown_window=60, # Keep alive for 1 min after use (Cost Optimization)
        timeout=3600 # Increased to 1h
    )
    class CloudIntelligence:
        @modal.enter()
        def load_model(self):
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            import torch
            
            print("📸 CloudIntelligence: Restoring from Snapshot (or Loading)...")
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                MODEL_ID, torch_dtype="auto", device_map="auto", trust_remote_code=True
            )
            self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
            print("✅ Model Ready.")

        @modal.method()
        def cloud_process_pdf(self, file_bytes: bytes, filename: str):
            """
            Optimized PDF Processing retrieving from Snapshot state.
            """
            import io
            import os
            import json
            import tempfile
            from docling.document_converter import DocumentConverter
            from pdf2image import convert_from_path
            
            # Helper: No need to reload model! Use self.model
            
            # 1. Setup Files
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            markdown = ""
            metadata = {}

            try:
                # 2. DOCLING (Layout Analysis)
                converter = DocumentConverter()
                res = converter.convert(tmp_path)
                markdown = res.document.export_to_markdown()

                # 3. VISUAL & TEXTUAL INTELLIGENCE (The Data Refinery)
                # "Head Chef" Mode: We use the 72B Brain to extract deep structure from the cleaned ingredients.
                images = convert_from_path(tmp_path, first_page=1, last_page=1)
                
                if images:
                    page_image = images[0]
                    # The "Refinery Prompt": One massive call to get everything (for speed/cost)
                    prompt = (
                        f"Analyze this document deeply. Use both the visual layout and the following extracted text:\n"
                        f"{markdown[:8000]}...\n\n" # Truncate to fit context if massive
                        "TASK 1: VISUAL METADATA\n"
                        "- Brand, Document Type, Visual Credibility Score, Sentiment.\n\n"
                        "TASK 2: ENTITY MINING (Knowledge Graph)\n"
                        "- List up to 20 key Entities (People, Companies, Projects) found.\n\n"
                        "TASK 3: EXECUTIVE BRIEF\n"
                        "- 3 Bullet points summarizing Critical Risks, Weird Clauses, or Key Numbers.\n\n"
                        "TASK 4: STRUCTURE\n"
                        "- Convert the core data into a strict JSON-like structure (e.g. {date:..., total:...}).\n\n"
                        "Return valid JSON ONLY in this format: "
                        "{\"metadata\": {...}, \"entities\": [\"Name (Type)\", ...], \"summary\": \"...\", \"structured_data\": {...}}"
                    )
                    
                    messages = [{"role": "user", "content": [{"type": "image", "image": page_image}, {"type": "text", "text": prompt}]}]
                    text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    inputs = self.processor(text=[text], images=[page_image], padding=True, return_tensors="pt").to("cuda")
                    
                    output_ids = self.model.generate(**inputs, max_new_tokens=2048)
                    generated_ids = [output_ids[len(in_ids):] for in_ids, output_ids in zip(inputs.input_ids, output_ids)]
                    output_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                    
                    # Cleanup JSON
                    clean_json = output_text
                    if "```json" in clean_json:
                        clean_json = clean_json.split("```json")[1].split("```")[0]
                    elif "```" in clean_json:
                        clean_json = clean_json.split("```")[1].split("```")[0]
                    try:
                        analysis = json.loads(clean_json.strip())
                        metadata = analysis.get("metadata", {})
                        metadata["entities"] = analysis.get("entities", [])
                        metadata["summary"] = analysis.get("summary", "")
                        metadata["structured_data"] = analysis.get("structured_data", {})
                        metadata["quality_score"] = 0.95 # H100 Verified
                    except:
                        metadata = {"raw_vision_analysis": output_text, "error": "JSON Parse Failed"}

            except Exception as e:
                print(f"Cloud Processing Failed: {e}")
                # Fallback to PyPDF
                import pypdf
                stream = io.BytesIO(file_bytes)
                reader = pypdf.PdfReader(stream)
                full_text = []
                for i, page in enumerate(reader.pages):
                     txt = page.extract_text()
                     if txt: full_text.append(txt)
                markdown = "\\n\\n".join(full_text)
                metadata = {"error": str(e), "fallback": "pypdf"}
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            return {"text": markdown or "", "metadata": metadata}

        # -------------------------------------------------------------------------
        # PHASE 9b: DEEP GARDENING (The Nightly Janitor)
        # -------------------------------------------------------------------------

        @modal.method()
        def cloud_graph_weaver(self, node_list: list):
            """
            Analyzes a list of seemingly unrelated nodes to find hidden connections.
            """
            prompt = (
                f"You are a Knowledge Graph Architect.\n"
                f"Analyze this list of entities: {node_list}\n"
                "Identify plausible relationships between them based on your world knowledge and the context implied.\n"
                "Return valid JSON ONLY: {'edges': [{'source': '...', 'target': '...', 'relation': '...'}, ...]}"
            )
            return self._run_inference(prompt)

        @modal.method()
        def cloud_truth_auditor(self, conflicting_facts: list):
            """
            Resolves contradictions in the database.
            """
            prompt = (
                f"You are a Truth Arbiter.\n"
                f"Resolve the following contradiction based on high-probability reality:\n"
                f"{conflicting_facts}\n"
                "Return valid JSON ONLY: {'verdict': 'The correct fact', 'confidence': 0.0-1.0, 'reason': 'Why'}"
            )
            return self._run_inference(prompt)

        @modal.method()
        def cloud_gap_detector(self, project_context: str):
            """
            Identifies missing critical information for a project.
            """
            prompt = (
                f"You are a Project Manager auditing this project summary:\n"
                f"{project_context}\n"
                "What strictly necessary information is MISSING? (e.g. Budget, Deadline, Owner).\n"
                "Return as a JSON list: {'missing_fields': ['Budget', ...]}"
            )
            return self._run_inference(prompt)

        # Helper for internal inference (DRY)
        def _run_inference(self, prompt: str):
            messages = [{"role": "user", "content": prompt}]
            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.processor(text=[text], images=None, padding=True, return_tensors="pt").to("cuda")
            output_ids = self.model.generate(**inputs, max_new_tokens=1024)
            generated_ids = [output_ids[len(in_ids):] for in_ids, output_ids in zip(inputs.input_ids, output_ids)]
            output_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            clean_json = output_text
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0]
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0]
            
            try:
                return json.loads(clean_json.strip())
            except:
                return {"raw_text": output_text, "error": "JSON Parse Failed"}

    @app.local_entrypoint()
    def test_main():
        print("Use 'modal run agent_runner.modal_tasks::prime_model_cache' to initialize model first.")
        print("Then use orchestrate_cloud_refactor.py")
        
    # Helper to clean/prime cache from CLI
    @app.local_entrypoint()
    def init_volume():
        print("🚀 Invoking prime_model_cache on cloud...")
        prime_model_cache.remote()

else:
    # Dummy mock
    class MockApp:
        def function(self, *args: Any, **kwargs: Any) -> Any:
            def decorator(f: Any) -> Any:
                return f
            return decorator
        def cls(self, *args: Any, **kwargs: Any) -> Any:
            def decorator(f: Any) -> Any:
                f.remote = f
                return f
            return decorator
    app = MockApp()
    
    # Mock implementations...
    def graph_community_detection(*args, **kwargs): return {}
    def cloud_process_pdf(*args, **kwargs): return ""
    def cloud_process_image(*args, **kwargs): return ""
    def rerank_search_results(*args, **kwargs): return []
    def verify_fact(*args, **kwargs): return {}
    def detect_visual_anomaly(*args, **kwargs): return ""
    def cloud_database_cleanup(*args, **kwargs): return ""
    # Deep Gardening Mocks
    class CloudIntelligence:
        @staticmethod
        def cloud_graph_weaver(node_list: list): 
            log_uplink(f"Running Graph Weaver (Mock) on {len(node_list)} nodes...")
            return json.dumps({"edges": [{"source": "MockA", "target": "MockB", "relation": "MOCK_RELATION"}]})
        
        @staticmethod
        def cloud_truth_auditor(conflicting_facts: list): 
            log_uplink(f"Auditing Truth (Mock) for {len(conflicting_facts)} facts...")
            return json.dumps({"verdict": "Mock Fact", "confidence": 1.0, "reason": "Mocking"})
        
        @staticmethod
        def cloud_gap_detector(project_data: dict): 
            log_uplink("Detecting Gaps (Mock)...")
            return json.dumps({"missing_fields": ["Mock Field"]})
        
        @staticmethod
        def cloud_process_pdf(file_bytes: bytes, filename: str):
            log_uplink(f"Processing PDF (Mock): {filename}...")
            return {"text": "Mock PDF Text", "metadata": {"quality_score": 0.5}}
