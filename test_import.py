import traceback
try:
    from app.agents.orchestrator import create_market_agent
except Exception as e:
    with open("import_error.txt", "w") as f:
        traceback.print_exc(file=f)
