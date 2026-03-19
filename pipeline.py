#!/usr/bin/env python3
"""
End-to-End Execution Pipeline
Cloud Service Providers Use Case

Runs the entire workflow:
1. Generate raw dirty datasets
2. Execute data cleaning via the cleaning notebook
3. Execute analytics and metric generations via the transform notebook
"""

import os
import subprocess
import sys

def run_command(cmd, step_name):
    print(f"\n{'='*70}")
    print(f" 🚀 PIPELINE STEP: {step_name}")
    print(f"{'='*70}")
    try:
        # We stream output natively to console
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during {step_name}. Halting pipeline.")
        sys.exit(1)

def main():
    # Determine the safest python and jupyter binaries depending on virtual environments
    py_cmd = "python3"
    jupyter_cmd = "jupyter"
    if os.path.exists("venv/bin/python"):
        py_cmd = "venv/bin/python"
    if os.path.exists("venv/bin/jupyter"):
        jupyter_cmd = "venv/bin/jupyter"
        
    # 1. Generate Synthetic Datasets
    run_command(f"{py_cmd} generate_dataset.py", "Generating Raw Dirty Dataset")
    
    # 2. Execute Cleaning Layer
    run_command(f"{jupyter_cmd} nbconvert --execute --inplace cleaning_notebook.ipynb", "Executing Cleaning Notebook")
    
    # 3. Execute Transformation Layer
    run_command(f"{jupyter_cmd} nbconvert --execute --inplace transform_notebook.ipynb", "Executing Transformation Notebook")
    
    print("\n✅ Pipeline Execution Completed Successfully!")
    print("   ↳ Cleaned data available in:  data/cleaned/")
    print("   ↳ Transformations available in: data/transforms/")
    print("   ↳ Notebook graphics have been updated.")

if __name__ == "__main__":
    main()
