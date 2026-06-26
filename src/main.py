import sys
from simulator import TinyBASU_Simulator

def main():
    if len(sys.argv) != 6:
        print("Usage: python main.py timeout_cycles prediction_method inst_file data_file report_file")
        print("مثال: python main.py 1000 ST asm/fibo_bne.asm data.txt reports/fibo_bne_st.txt")
        return

    timeout_cycles = int(sys.argv[1])
    prediction_method = sys.argv[2]
    inst_file = sys.argv[3]
    data_file = sys.argv[4]
    report_file = sys.argv[5]

    sim = TinyBASU_Simulator(prediction_method)
    sim.init_memory(inst_file, data_file)
    sim.simulate(timeout_cycles)
    sim.report(report_file)
    print(f"✅ گزارش با موفقیت در {report_file} ذخیره شد.")

if __name__ == "__main__":
    main()