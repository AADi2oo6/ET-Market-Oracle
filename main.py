import uvicorn
from app.main import app

def main():
    """Runs the FastAPI backend using uvicorn."""
    print("Starting ET Market Oracle Backend on port 8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
