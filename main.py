import warnings
# Suppress Pandas FutureWarning (Timestamp.utcnow)
warnings.simplefilter(action='ignore', category=FutureWarning)

from backend import screener
from backend import report_generator
import time

def main():
    start_time = time.time()
    print("=== Contrarian Stock Picker System Started ===")
    
    # 1. Run Screen
    candidates = screener.run_screen()
    
    # 2. Generate Report
    print(f"\nGenerating report for {len(candidates)} candidates...")
    report_file = report_generator.generate_markdown_report(candidates)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n=== Done in {duration:.1f} seconds ===")
    print(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()
