# 🖥️ TinyBASU instruction set simulator with a 5-stage pipeline execution model and branch prediction

<a id="overview"></a>
## Overview
A complete **5-stage pipeline processor simulator** for the **TinyBASU** architecture (a MIPS-like 16-bit processor) with **static and dynamic branch prediction** support. This project implements a full instruction set simulator (ISS) with built-in assembler, performance analysis tools, and automated batch testing for computer architecture education.

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Instruction Set](#instruction-set)
- [Branch Prediction Methods](#branch-prediction-methods)
- [Performance Metrics](#performance-metrics)
- [Installation & Usage](#installation--usage)
- [Batch Execution](#batch-execution)
- [Optional Extension](#optional-extension)
- [Simulation Results](#simulation-results)
- [Author](#author)
- [License](#license)

<br>

<a id="project-structure"></a>
## 📁 Project Structure

```
TinyBUSA/
│
├── 📂 asm/
│   ├── 📄fibonacci_bne.asm
│   ├── 📄fibonacci_beq.asm
│   └── 📄fact.asm
│
├── 📂 misc/
│   └── 📄new_instructions.asm
│
├── 📂 reports/
│   ├── 📄fibo_bne_*.txt
│   ├── 📄fibo_beq_*.txt
│   ├── 📄fact_*.txt
│   └── 📄new_instructions_*.txt
│
├── 📂 src/
│   ├── 📄main.py
│   └── 📄simulator.py
│
├── 📄.gitignore
└── 📝 LICENSE
├── 📝 README.md
├── 📜 data.txt
├── 📜 run_all.py
```

<a id="architecture"></a>
## 🧠 Architecture

### Processor Specifications

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 30%;">Component</th>
      <th style="padding: 10px; text-align: left; width: 70%;">Specification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Architecture</td>
      <td style="padding: 8px;">MIPS-like, 16-bit RISC</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Registers</td>
      <td style="padding: 8px;">8 × 16-bit (<code>r0</code> – <code>r7</code>), <code>r0</code> hardwired to zero</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Memory</td>
      <td style="padding: 8px;">512 × 16-bit (Instructions: 0–255, Data: 256–511)</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Pipeline Stages</td>
      <td style="padding: 8px;">5-stage (Fetch, Decode, Execute, Memory, Writeback)</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Branch Penalty</td>
      <td style="padding: 8px;">3 cycles (for taken branches and mispredictions)</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Instruction Formats</td>
      <td style="padding: 8px;">R-type, I-type, J-type</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Immediate Size</td>
      <td style="padding: 8px;">6 bits (I-type) / 3 bits (R-type func) / 12 bits (J-type offset)</td>
    </tr>
  </tbody>
</table>

### Pipeline Behavior

- **Fetch**: Read instruction from memory at `PC`, increment `PC += 1`
- **Decode**: Extract opcode, registers, and immediate values
- **Execute**: Perform ALU operation or calculate branch target
- **Memory**: Load/Store data (only for `lw`/`sw` instructions)
- **Writeback**: Write result to register file

**Branch Penalty:**  
When a branch is taken (or mispredicted), the 3 instructions already fetched in the pipeline are flushed, causing a **3-cycle stall**.

<br>

<a id="instruction-set"></a>
## 📜 Instruction Set

### Base Instructions (TinyBASU ISA)

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left;">Type</th>
      <th style="padding: 10px; text-align: left;">Instruction</th>
      <th style="padding: 10px; text-align: left;">Opcode</th>
      <th style="padding: 10px; text-align: left;">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color: #f9f9f9; font-weight: bold;">
      <td rowspan="3" style="padding: 8px;">R-type</td>
      <td style="padding: 8px;"><code>add rd, rs, rt</code></td>
      <td style="padding: 8px;">0 / func=1</td>
      <td style="padding: 8px;"><code>rd = rs + rt</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>sub rd, rs, rt</code></td>
      <td style="padding: 8px;">0 / func=2</td>
      <td style="padding: 8px;"><code>rd = rs - rt</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>slt rd, rs, rt</code></td>
      <td style="padding: 8px;">0 / func=4</td>
      <td style="padding: 8px;"><code>rd = 1 if rs &lt; rt else 0</code></td>
    </tr>
    <tr>
      <td rowspan="5" style="padding: 8px;">I-type</td>
      <td style="padding: 8px;"><code>addi rd, rs, imm</code></td>
      <td style="padding: 8px;">1</td>
      <td style="padding: 8px;"><code>rd = rs + imm</code> (6-bit immediate)</td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>li rd, imm</code></td>
      <td style="padding: 8px;">2</td>
      <td style="padding: 8px;"><code>rd = imm</code> (load immediate)</td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>lui rd, imm</code></td>
      <td style="padding: 8px;">3</td>
      <td style="padding: 8px;"><code>rd = imm << 10</code> (load upper immediate)</td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>lw rd, rs, imm</code></td>
      <td style="padding: 8px;">4</td>
      <td style="padding: 8px;"><code>rd = mem[rs + imm]</code></td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>sw rd, rs, imm</code></td>
      <td style="padding: 8px;">5</td>
      <td style="padding: 8px;"><code>mem[rs + imm] = rd</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td rowspan="2" style="padding: 8px;">Branches</td>
      <td style="padding: 8px;"><code>beq rd, rs, label</code></td>
      <td style="padding: 8px;">10</td>
      <td style="padding: 8px;">Branch if <code>rs == rd</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>bne rd, rs, label</code></td>
      <td style="padding: 8px;">11</td>
      <td style="padding: 8px;">Branch if <code>rs != rd</code></td>
    </tr>
    <tr>
      <td rowspan="2" style="padding: 8px;">Jumps</td>
      <td style="padding: 8px;"><code>jmp label</code></td>
      <td style="padding: 8px;">14</td>
      <td style="padding: 8px;">Unconditional jump</td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>jal label</code></td>
      <td style="padding: 8px;">15</td>
      <td style="padding: 8px;">Jump and link (<code>r7 = PC+1</code>)</td>
    </tr>
  </tbody>
</table>

<br>

<a id="branch-prediction-methods"></a>
## 🔮 Branch Prediction Methods

The simulator supports **5 different branch prediction algorithms**:

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #2196F3; color: white;">
      <th style="padding: 10px; text-align: left;">Method</th>
      <th style="padding: 10px; text-align: left;">Identifier</th>
      <th style="padding: 10px; text-align: left;">Type</th>
      <th style="padding: 10px; text-align: left;">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Always Taken</td>
      <td style="padding: 8px;"><code>ST</code></td>
      <td style="padding: 8px;">Static</td>
      <td style="padding: 8px;">Always predicts branch will be taken</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Always Not Taken</td>
      <td style="padding: 8px;"><code>SN</code></td>
      <td style="padding: 8px;">Static</td>
      <td style="padding: 8px;">Always predicts branch will not be taken</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">1-bit Dynamic</td>
      <td style="padding: 8px;"><code>D1</code></td>
      <td style="padding: 8px;">Dynamic</td>
      <td style="padding: 8px;">2-state saturating counter; flips on misprediction</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">2-bit Dynamic</td>
      <td style="padding: 8px;"><code>D2</code></td>
      <td style="padding: 8px;">Dynamic</td>
      <td style="padding: 8px;">4-state saturating counter; changes after 2 mispredictions</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Innovative 3-bit</td>
      <td style="padding: 8px;"><code>IQ</code></td>
      <td style="padding: 8px;">Dynamic</td>
      <td style="padding: 8px;">8-state saturating counter (custom method)</td>
    </tr>
  </tbody>
</table>

### State Machines

**1️⃣bit Predictor (D1):**
- 2 states: `0` (Not Taken), `1` (Taken)
- Flips on every misprediction

**2️⃣bit Predictor (D2):**
- 4 states: `00` (Strong Not Taken), `01` (Weak Not Taken), `10` (Weak Taken), `11` (Strong Taken)
- Only changes after 2 consecutive mispredictions

**3️⃣bit Predictor (IQ):**
- 8 states: `0` to `7`
- Saturating counter (increments on taken, decrements on not taken)

<br>

<a id="performance-metrics"></a>
## 📊 Performance Metrics

Each simulation run generates a comprehensive report with the following metrics:

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 30%;">Metric</th>
      <th style="padding: 10px; text-align: left; width: 70%;">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Simulator Runtime</td>
      <td style="padding: 8px;">Wall-clock time of the simulation</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Number of Assembly Instructions</td>
      <td style="padding: 8px;">Static instruction count in the assembly file</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Number of Cycles</td>
      <td style="padding: 8px;">Total clock cycles to execute the program</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Number of Executed Commands</td>
      <td style="padding: 8px;">Dynamic instruction count (including repeated loops)</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">IPC</td>
      <td style="padding: 8px;"><code>Instructions Per Cycle = Executed Commands / Cycles</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Number of Stalls</td>
      <td style="padding: 8px;">Total branch penalty stalls (3 cycles each)</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Number of Jumps</td>
      <td style="padding: 8px;">Total branch/jump instructions encountered</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Prediction Precision</td>
      <td style="padding: 8px;">Percentage of correctly predicted branches</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Speedup</td>
      <td style="padding: 8px;">Speedup compared to no branch prediction (baseline)</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Final Registers</td>
      <td style="padding: 8px;">Contents of all 8 registers after execution</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">PC</td>
      <td style="padding: 8px;">Final Program Counter value</td>
    </tr>
  </tbody>
</table>

<br>

<a id="installation--usage"></a>
## 🚀 Installation & Usage

### Prerequisites
- **Python 3.6+** (with standard library only)
- No external dependencies required

### Running a Single Test
```bash
python main.py [timeout] [prediction_method] [inst_file] [data_file] [report_file]
```

**Example:**
```bash
python main.py 10000 ST asm/fibonacci_bne.asm data.txt Reports/fibo_bne_st.txt
```

**Arguments:**
- `timeout`: Maximum cycles to prevent infinite loops (e.g., 10000)
- `prediction_method`: One of `ST`, `SN`, `D1`, `D2`, `IQ`
- `instruction_file`: Path to assembly file (e.g., `asm/fibonacci_bne.asm`)
- `data_file`: Path to data memory file (e.g., `data.txt`)
- `report_file`: Output report path (e.g., `reports/fibo_bne_st.txt`)

### Running All Tests (Batch Mode)
```bash
python run_all.py
```

This automatically executes **20 test cases**:
- 5 prediction methods × 3 base programs = 15 reports
- 5 prediction methods × 1 optional program = 5 additional reports

All reports are saved in the `reports/` folder with standardized naming.

<a id="batch-execution"></a>
## ⚙️ Batch Execution

`run_all.py` automatically runs all combinations of programs and prediction methods:

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 30%;">Program</th>
      <th style="padding: 10px; text-align: center; width: 40%;">Prediction Methods</th>
      <th style="padding: 10px; text-align: center; width: 30%;">Reports</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px;"><code>fibonacci_bne.asm</code></td>
      <td style="padding: 8px; text-align: center;"><code>ST, SN, D1, D2, IQ</code></td>
      <td style="padding: 8px; text-align: center;"><code>fibo_bne_*.txt</code> (5)</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>fibonacci_beq.asm</code></td>
      <td style="padding: 8px; text-align: center;"><code>ST, SN, D1, D2, IQ</code></td>
      <td style="padding: 8px; text-align: center;"><code>fibo_beq_*.txt</code> (5)</td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>fact.asm</code></td>
      <td style="padding: 8px; text-align: center;"><code>ST, SN, D1, D2, IQ</code></td>
      <td style="padding: 8px; text-align: center;"><code>fact_*.txt</code> (5)</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>new_instructions.asm</code> (optional)</td>
      <td style="padding: 8px; text-align: center;"><code>ST, SN, D1, D2, IQ</code></td>
      <td style="padding: 8px; text-align: center;"><code>new_instructions_*.txt</code> (5)</td>
    </tr>
    <tr style="background-color: #e0e0e0; font-weight: bold;">
      <td style="padding: 8px; text-align: center;">Total</td>
      <td style="padding: 8px; text-align: center;"></td>
      <td style="padding: 8px; text-align: center;">20 reports</td>
    </tr>
  </tbody>
</table>

<br>

<a id="optional-extension"></a>
## ✨ Optional Extension: 10 New Instructions

As part of the project's extra credit module, **10 new instructions** were added to the simulator:

### R-type New Instructions

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 25%;">Instruction</th>
      <th style="padding: 10px; text-align: center; width: 10%;">Function</th>
      <th style="padding: 10px; text-align: left; width: 40%;">Description</th>
      <th style="padding: 10px; text-align: left; width: 25%;">Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px;"><code>mul rd, rs, rt</code></td>
      <td style="padding: 8px; text-align: center;">3</td>
      <td style="padding: 8px;">Multiply: <code>rd = rs &times; rt</code></td>
      <td style="padding: 8px;"><code>mul r3, r1, r2</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>div rd, rs, rt</code></td>
      <td style="padding: 8px; text-align: center;">5</td>
      <td style="padding: 8px;">Integer division: <code>rd = rs &divide; rt</code></td>
      <td style="padding: 8px;"><code>div r4, r3, r2</code></td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>sll rd, rs, rt</code></td>
      <td style="padding: 8px; text-align: center;">6</td>
      <td style="padding: 8px;">Shift left logical: <code>rd = rs &lt;&lt; rt</code></td>
      <td style="padding: 8px;"><code>sll r5, r1, r2</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>srl rd, rs, rt</code></td>
      <td style="padding: 8px; text-align: center;">7</td>
      <td style="padding: 8px;">Shift right logical: <code>rd = rs &gt;&gt; rt</code></td>
      <td style="padding: 8px;"><code>srl r5, r5, r2</code></td>
    </tr>
  </tbody>
</table>

### I-type New Instructions

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 25%;">Instruction</th>
      <th style="padding: 10px; text-align: center; width: 10%;">Opcode</th>
      <th style="padding: 10px; text-align: left; width: 40%;">Description</th>
      <th style="padding: 10px; text-align: left; width: 25%;">Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px;"><code>slli rd, rs, imm</code></td>
      <td style="padding: 8px; text-align: center;">6</td>
      <td style="padding: 8px;">Shift left logical immediate</td>
      <td style="padding: 8px;"><code>slli r0, r1, 2</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>srli rd, rs, imm</code></td>
      <td style="padding: 8px; text-align: center;">7</td>
      <td style="padding: 8px;">Shift right logical immediate</td>
      <td style="padding: 8px;"><code>srli r0, r0, 1</code></td>
    </tr>
    <tr>
      <td style="padding: 8px;"><code>andi rd, rs, imm</code></td>
      <td style="padding: 8px; text-align: center;">8</td>
      <td style="padding: 8px;">Bitwise AND immediate</td>
      <td style="padding: 8px;"><code>andi r0, r3, 15</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>ori rd, rs, imm</code></td>
      <td style="padding: 8px; text-align: center;">9</td>
      <td style="padding: 8px;">Bitwise OR immediate</td>
      <td style="padding: 8px;"><code>ori r0, r0, r1</code></td>
    </tr>
  </tbody>
</table>

### New Branch Instructions

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 25%;">Instruction</th>
      <th style="padding: 10px; text-align: center; width: 10%;">Opcode</th>
      <th style="padding: 10px; text-align: left; width: 40%;">Description</th>
      <th style="padding: 10px; text-align: left; width: 25%;">Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px;"><code>bltz rs, label</code></td>
      <td style="padding: 8px; text-align: center;">12</td>
      <td style="padding: 8px;">Branch if <code>rs &lt; 0</code></td>
      <td style="padding: 8px;"><code>bltz r1, done</code></td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px;"><code>bgtz rs, label</code></td>
      <td style="padding: 8px; text-align: center;">13</td>
      <td style="padding: 8px;">Branch if <code>rs &gt; 0</code></td>
      <td style="padding: 8px;"><code>bgtz r7, sum_loop</code></td>
    </tr>
  </tbody>
</table>

### Test Program: `new_instructions.asm`

A comprehensive test program validates all 10 new instructions, including:
- Arithmetic operations (multiplication, division)
- Shift operations (logical left/right, immediate versions)
- Bitwise operations (AND, OR)
- Branching with sign checks (`bltz`, `bgtz`)
- A loop that calculates the sum of 10 to 1 (accumulated sum)

<br>

<a id="simulation-results"></a>
## 📈 Simulation Results Summary

### Best Performance per Program

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #4CAF50; color: white;">
      <th style="padding: 10px; text-align: left; width: 25%;">Program</th>
      <th style="padding: 10px; text-align: center; width: 15%;">Best Method</th>
      <th style="padding: 10px; text-align: center; width: 20%;">IPC</th>
      <th style="padding: 10px; text-align: center; width: 20%;">Accuracy</th>
      <th style="padding: 10px; text-align: center; width: 20%;">Speedup</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Fibonacci (BNE)</td>
      <td style="padding: 8px; text-align: center;"><code>ST</code></td>
      <td style="padding: 8px; text-align: center;">0.9797</td>
      <td style="padding: 8px; text-align: center; color: green; font-weight: bold;">96.43%</td>
      <td style="padding: 8px; text-align: center;">1.5473x</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">Fibonacci (BEQ)</td>
      <td style="padding: 8px; text-align: center;"><code>D1/D2/IQ/SN</code></td>
      <td style="padding: 8px; text-align: center;">0.6719</td>
      <td style="padding: 8px; text-align: center; color: orange; font-weight: bold;">49.09%</td>
      <td style="padding: 8px; text-align: center;">1.3164x</td>
    </tr>
    <tr>
      <td style="padding: 8px; font-weight: bold;">Factorial</td>
      <td style="padding: 8px; text-align: center;"><code>ST</code></td>
      <td style="padding: 8px; text-align: center;">0.9340</td>
      <td style="padding: 8px; text-align: center; color: green; font-weight: bold;">92.57%</td>
      <td style="padding: 8px; text-align: center;">1.8230x</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 8px; font-weight: bold;">New Instructions</td>
      <td style="padding: 8px; text-align: center;"><code>ST</code></td>
      <td style="padding: 8px; text-align: center;">0.9388</td>
      <td style="padding: 8px; text-align: center; color: green; font-weight: bold;">90.91%</td>
      <td style="padding: 8px; text-align: center;">1.6122x</td>
    </tr>
  </tbody>
</table>

### Observations

- **Static prediction (ST)** performs exceptionally well for loops where the branch is almost always taken.
- **Dynamic predictors (D1/D2/IQ)** adapt well to changing branch patterns but may suffer from cold-start mispredictions.
- **Static prediction (SN)** consistently underperforms, with accuracy below 10% for loop-heavy programs.
- The **2-bit predictor (D2)** generally outperforms the 1-bit predictor (D1) for programs with repetitive branch patterns.

<br>

<a id="author"></a>
## 👤 Author

Tiny BASU project Implemented by [Pouyamaleki](https://github.com/Pouyamaleki)  
Computer Architecture Project – summer 2026  
Supervised by: Dr. Mehdi Abbasi

<a id="license"></a>
## 📝 License

MIT License - feel free to use, learn, and improve!
