#this code is Written by the AI for the easier excution!!!!!!!!

import os
import subprocess

# ==================================================
# Configuration Section
# ==================================================

# Simulation parameters
TIMEOUT_CYCLES = "10000"        # Maximum cycles to prevent infinite loops
DATA_FILE = "data.txt"          # Data memory file (can be empty)

# Folder paths
ASM_FOLDER = "asm"              # Folder containing assembly files
REPORTS_FOLDER = "Reports"      # Folder to save the output reports

# List of assembly programs to test
# Format: (assembly_filename, base_name_for_report)
programs = [
    ("fibo_bne.asm", "fibo_bne"),
    ("fibo_beq.asm", "fibo_beq"),
    ("fact.asm", "fact")
]

# List of branch prediction methods to evaluate
methods = ["ST", "SN", "D1", "D2", "IQ"]

# ==================================================
# Execution Loop
# ==================================================

# Ensure the reports folder exists (optional, but safe)
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)
    print(f"📁 Created folder: {REPORTS_FOLDER}")

print("🚀 Starting the batch simulation for all programs...\n")

# Loop through each program
for asm_file, base_name in programs:
    # Loop through each prediction method
    for method in methods:
        # Construct the report file name (e.g., fibo_bne_st.txt)
        # The project specification requires lowercase method names in the file
        report_file = f"{REPORTS_FOLDER}/{base_name}_{method.lower()}.txt"
        
        # Build the command line instruction
        # Format: python main.py [timeout] [method] [inst_file] [data_file] [report_file]
        cmd = (
            f"python ../main.py ..."
            f"{TIMEOUT_CYCLES} "
            f"{method} "
            f"{ASM_FOLDER}/{asm_file} "
            f"{DATA_FILE} "
            f"{report_file}"
        )
        
        # Print the command being executed (for tracking progress)
        print(f"⏳ Executing: {cmd}")
        
        # Run the command and wait for it to finish
        # Using subprocess.call gives better control than os.system
        exit_code = subprocess.call(cmd, shell=True)
        
        # Check if the command executed successfully
        if exit_code == 0:
            print(f"✅ Successfully generated: {report_file}")
        else:
            print(f"❌ Error occurred while generating: {report_file}")
        
        print("-" * 60)  # Separator line for readability

print("\n🎉 All 15 reports have been generated successfully!")
print(f"📂 Check the '{REPORTS_FOLDER}' folder for the results.")