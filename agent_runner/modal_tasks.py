
import logging
import json
import os

# Try importing modal
try:
    import modal
    has_modal = True
except ImportError:
    has_modal = False

logger = logging.getLogger("agent_runner.modal")

# We define the App. 
# Important: If Modal is not installed, we create a dummy to prevent import errors.
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


else:
    # Dummy mock
    class MockApp:
        def function(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    app = MockApp()
    
    def graph_community_detection(*args, **kwargs):
        logger.warning("Modal library not found. Skipping Cloud Graph Processing.")
        return {}
    
    def cloud_heavy_reasoning(*args, **kwargs):
        return {"result": "Modal not active."}
