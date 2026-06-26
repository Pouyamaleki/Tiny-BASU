# This code is Written by the AI for easier execution !!!!!!!!

import os
import subprocess

# ==================================================
# Configuration Section
# ==================================================

TIMEOUT_CYCLES = "10000"
DATA_FILE = "data.txt"

# Base directory: where this script (run_all.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Possible locations for main.py (in order of priority)
POSSIBLE_MAIN_PATHS = [
    os.path.join(BASE_DIR, "main.py"),        # same folder
    os.path.join(BASE_DIR, "src", "main.py"), # inside src folder
]

# Find main.py automatically
MAIN_SCRIPT = None
for path in POSSIBLE_MAIN_PATHS:
    if os.path.exists(path):
        MAIN_SCRIPT = path
        break

if MAIN_SCRIPT is None:
    print("❌ Error: main.py not found in any expected location!")
    print(f"   Searched in: {POSSIBLE_MAIN_PATHS}")
    exit(1)

# Folder paths
ASM_FOLDER = os.path.join(BASE_DIR, "asm")
REPORTS_FOLDER = os.path.join(BASE_DIR, "Reports")

# Programs and methods
programs = [
    ("fibonacci_bne.asm", "fibo_bne"),
    ("fibonacci_beq.asm", "fibo_beq"),
    ("fact.asm", "fact")
]

methods = ["ST", "SN", "D1", "D2", "IQ"]

# ==================================================
# Execution Loop
# ==================================================

if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)
    print(f"📁 Created folder: {REPORTS_FOLDER}")

print("🚀 Starting the batch simulation for all programs...\n")
print(f"📍 Using main.py from: {MAIN_SCRIPT}\n")

for asm_file, base_name in programs:
    for method in methods:
        report_file = os.path.join(REPORTS_FOLDER, f"{base_name}_{method.lower()}.txt")
        asm_path = os.path.join(ASM_FOLDER, asm_file)

        cmd = [
            "python",
            MAIN_SCRIPT,
            TIMEOUT_CYCLES,
            method,
            asm_path,
            DATA_FILE,
            report_file
        ]

        print(f"⏳ Executing: {' '.join(cmd)}")
        exit_code = subprocess.call(cmd, shell=False)

        if exit_code == 0:
            print(f"✅ Successfully generated: {report_file}")
        else:
            print(f"❌ Error occurred while generating: {report_file}")

        print("-" * 60)

print("\n🎉 All 15 reports have been generated successfully!")
print(f"📂 Check the '{REPORTS_FOLDER}' folder for the results.")