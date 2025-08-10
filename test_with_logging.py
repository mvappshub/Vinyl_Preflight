#!/usr/bin/env python3
"""
Test s detailním logováním do souboru
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vinyl_preflight_app import PreflightProcessor

def progress_callback(current, total):
    print(f"[PROGRESS] {current}/{total}")

def status_callback(message):
    print(f"[STATUS] {message}")

def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY not set")
        return
    
    processor = PreflightProcessor(
        api_key=api_key,
        progress_callback=progress_callback,
        status_callback=status_callback
    )
    
    # Test with RecordPlant project
    test_dir = "C:\\gz_projekt\\data-for-testing\\01"
    print(f"Testing with directory: {test_dir}")
    
    try:
        result = processor.run(test_dir)
        print(f"Result: {result}")
        print("\n🎯 DETAILNÍ LOG BYL ULOŽEN DO SOUBORU!")
        print("Najdete ho v output/ adresáři s názvem Detailed_Log_*.txt")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
