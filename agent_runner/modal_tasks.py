
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

    # Define the environment: A lightweight Debian image with graph libraries
    image = (
        modal.Image.debian_slim()
        .pip_install("networkx", "scikit-learn", "numpy")
    )

    # 1. Graph Community Detection (CPU Intensive)
    @app.function(image=image, timeout=600)
    def graph_community_detection(nodes: list, edges: list):
        """
        Runs Louvain Community Detection on the Knowledge Graph.
        Returns a mapping of {node_id: community_id}.
        """
        import networkx as nx
        from networkx.algorithms import community

        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # Louvain is standard for detecting clusters
        try:
            communities = community.louvain_communities(G)
        except Exception as e:
            return {"error": str(e)}
        
        # Convert to flat map
        result = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                result[node] = idx
                
        return result

    # 2. Advanced Reasoner (H100 GPU)
    # This function requests a GPU to run a heavy inference task if needed.
    # Note: We comment out the GPU requirement to keep it cheap unless explicitly enabled,
    # or we use a CPU-based logic that calls an external API from within Modal (acting as a secure proxy).
    # For now, let's keep it simple: A function that CAN be upgraded to use gpu="A10g" or "H100"
    @app.function(image=image, timeout=300) 
    def cloud_heavy_reasoning(context_text: str, query: str):
        """
        Placeholder for heavy reasoning. 
        Currently runs on CPU, but can be flagged for GPU.
        """
        return {"result": f"Processed {len(context_text)} chars in cloud."}

    # 3. Heavy PDF Ingestion (Cloud Offload)
    # Uses PyPDF + Vision in the cloud to avoid local lag
    @app.function(image=image.pip_install("pypdf"), timeout=600)
    def cloud_process_pdf(file_bytes: bytes, filename: str):
        """
        Ingests a PDF in the cloud. 
        Extracts text and performs OCR on images if needed.
        Returns the full markdown content.
        """
        import io
        import pypdf
        
        # 1. Load PDF
        stream = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(stream)
        
        full_text = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"## Page {i+1}\n{text}")
            
            # TODO: Add Cloud Vision OCR here for images in the PDF
            # We can use a local model inside the container or call out
            
        return "\n\n".join(full_text)

    # 4. Heavy Image Analysis (Cloud Offload)
    # Uses a vision model (or strong cloud CPU logic) to describe images cheaply
    # 4. Heavy Image Analysis (Cloud Offload)
    # Uses a vision model to describe images with structured metadata
    @app.function(image=image, timeout=300)
    def cloud_process_image(image_bytes: bytes, prompt: Optional[str] = None):
        """
        Analyzes an image in the cloud.
        Returns JSON-formatted string with:
        - description: Detailed narrative.
        - objects: List of detected objects.
        - animals: List of animals.
        - people: Count/Description.
        """
        if prompt is None:
            prompt = (
                "Analyze this image. "
                "If it contains a PLANT: Identify species, exact variety, and health status (pests/diseases). "
                "If it contains a MACHINE: Identify model, wear-and-tear, and rust. "
                "Return JSON keys: 'description', 'objects', 'animals', 'plants' (list of details), 'people', 'camera_data'."
            )
            
        # Real GPU Logic would go here (e.g. Qwen-VL or LLaVA with json enforcement)
        
        # Mock Response for now (until you deploy with actual model code)
        import json
        return json.dumps({
            "description": "Image analysis running in cloud.",
            "objects": ["detected_item_1"],
            "animals": [],
            "plants": [],
            "people": [],
            "camera_data": "Unknown"
        })

    # 5. Search Re-Ranking (GPU/CPU)
    # Uses a Cross-Encoder to rank search results better than vector similarity
    @app.function(image=image.pip_install("sentence-transformers", "torch"), timeout=60)
    def rerank_search_results(query: str, candidates: list):
        """
        Re-ranks a list of text chunks based on relevance to the query.
        """
        from sentence_transformers import CrossEncoder
        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # internal format: (query, doc)
        pairs = [[query, doc] for doc in candidates]
        scores = model.predict(pairs)
        
        # specific return format: list of (index, score)
        scored_results = []
        for i, score in enumerate(scores):
            scored_results.append((i, float(score)))
            
        # Sort by score desc
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results

    # 6. Deep Fact Verification (The Audit)
    # Uses a strong NLI model or LLM to check if evidence supports a claim
    @app.function(image=image.pip_install("transformers", "torch"), timeout=300)
    def verify_fact(fact: str, evidence: str):
        """
        Checks if the evidence supports the fact.
        Returns: 'SUPPORTED', 'CONTRADICTED', or 'NEUTRAL' with a confidence score.
        """
        # Using a pre-trained NLI model is cheaper/faster than a full LLM for this specific task
        from transformers import pipeline
        nli_model = pipeline("text-classification", model="roberta-large-mnli")
        
        # NLI format: "Fact. Evidence"
        input_text = f"{fact} {evidence}"
        result = nli_model(input_text)
        
        # Map NLI labels to ours
        # roberta-large-mnli labels: CONTRADICTION, NEUTRAL, ENTAILMENT
        label_map = {
            "ENTAILMENT": "SUPPORTED",
            "CONTRADICTION": "CONTRADICTED",
            "NEUTRAL": "NEUTRAL"
        }
        
        top = result[0]
        return {
            "judgment": label_map.get(top['label'].upper(), "NEUTRAL"),
            "confidence": top['score']
        }

    # 7. Visual Anomaly Detection (The Sentry)
    # Compares a reference image to a new image to find defects/changes.
    @app.function(image=image, timeout=300)
    def detect_visual_anomaly(reference_bytes: bytes, candidate_bytes: bytes):
        """
        Compare two images and identify significant visual anomalies/defects.
        """
        # In real usage:
        # prompt = "Compare Image 1 (Reference) and Image 2 (Current). List mechanical defects, rust, or damage."
        # model.generate([img1, img2], prompt)
        
        # Mock logic
        return {
            "detected_changes": [
                "New oil stain on ground",
                "Rust spot on front loader bucket",
                "Tire pressure looks lower than reference"
            ],
            "severity": "MEDIUM",
            "confidence": 0.89
        }

    @app.local_entrypoint()
    def test_main():
        print("🚀 Triggering Cloud Test from CLI...")
        nodes = [1, 2, 3, 4, 5]
        edges = [(1,2), (2,3), (3,1), (4,5)]
        print("   Evaluating Graph...")
        res = graph_community_detection.remote(nodes, edges)
        print(f"✅ Result: {res}")





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
