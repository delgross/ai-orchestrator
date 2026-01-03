
import logging
import time
import os
import sys
import random
import uuid

# Ensure common is in path
sys.path.append(os.getcwd())

from common.logging_setup import setup_logger

def run_torture_test():
    print("😈 [Chaos Monkey] Initializing Diagnostic Torture Test...")
    
    # Setup Logger
    logger = setup_logger("chaos_monkey")
    
    # Scenario 1: The Known Signal Barrage (Fast Lane Test)
    # These should all be handled INSTANTLY and NOT trigger LLM.
    print("\n--- PHASE 1: KNOWN SIGNAL BARRAGE (20 Events) ---")
    print("Expected: Fast Lane processing, ZERO LLM calls.")
    for i in range(20):
        # Using a known pattern from lexicon (e.g., regex `Connection refused`)
        logger.error(f"[BUG] Database Connection Failed (Port {8000 + i}) - Connection refused")
        time.sleep(0.05) # simulate burst
    
    print("Phase 1 Complete. Waiting 5s for Sorter to catch up...")
    time.sleep(5)

    # Scenario 2: The Circuit Breaker Trip (Resilience Test)
    # These are random UNKNOWN errors. They SHOULD trigger LLM.
    # After 5 failures (or if we overload concurrency), the CB should trip.
    # Since we don't have a real LLM running locally (or we forced it to fail via 404 in previous test, 
    # but let's assume valid LLM for now, or ensure it fails to test CB).
    #
    # Note: If LLM is working, CB won't trip on failures, but Semaphore(2) will limit concurrency.
    # To FORCE CB trip, we need to simulate failure.
    # But let's just flood it and see if it handles the load gracefully.
    
    print("\n--- PHASE 2: CIRCUIT BREAKER STRESS TEST (10 Unique Unknowns) ---")
    print("Expected: First 2-5 trigger LLM. Subsequent requests throttled or queued.")
    
    for i in range(10):
        # Unique ID to bypass deduplication
        err_id = str(uuid.uuid4())[:8]
        logger.error(f"CRITICAL SYSTEM FAILURE {err_id}: Quantum Flux Capacitor Overload")
        time.sleep(0.2)
        
    print("Phase 2 Complete. Check logs/live_stream.md for AI Insights.")

    # Scenario 3: The Deduplication Test
    print("\n--- PHASE 3: DEDUPLICATION TEST (5 Identical Unknowns) ---")
    print("Expected: ONLY ONE AI Insight. 4 Duplicates ignored.")
    
    dedup_id = "DEDUP_" + str(uuid.uuid4())[:4]
    msg = f"Unknown Error {dedup_id}: Replicator Offline"
    
    for i in range(5):
        logger.error(msg)
        time.sleep(0.1)
        
    print("Phase 3 Complete.")
    print("Waiting 5s for DB flush...")
    time.sleep(5)
    print("\n😈 [Chaos Monkey] Torture Test Finished. Monitor the logs!")

if __name__ == "__main__":
    run_torture_test()
