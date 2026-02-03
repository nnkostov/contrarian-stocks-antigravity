import pandas as pd
from backend import screener

# Mock Data
price_data = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 48, 45, 42, 40]
df = pd.DataFrame({'Close': price_data})

# Test Technicals
print("--- Check Technicals ---")
metrics = screener.check_technicals(df)
print(f"Metrics: {metrics}")

# But check_fundamentals calls data_ingestion.fetch_stock_data. 
# So we effectively can't unit test check_fundamentals easily without mocking data_ingestion.
# However, we can verify check_technicals returns 'Reasons'.


if metrics and 'Rationale' in metrics:
    print("SUCCESS: Rationale narrative found in technical metrics.")
    print(metrics['Rationale'])
else:
    # Note: check_technicals doesn't call generate_narrative automatically based on my edit; 
    # run_screen does. So we need to call it manually here to test.
    print("Test Manual Narrative Generation:")
    metrics['Reasons'] = ['Mock Reason'] # Dummy
    metrics['PE'] = 12
    metrics['ProfitMargins'] = 0.25
    
    narrative = screener.generate_narrative("TEST", metrics)
    print(narrative)
    
    if "has come under significant pressure" in narrative:
        print("SUCCESS: Narrative generated correctly.")
    else:
        print("FAILURE: Narrative logic failed.")
