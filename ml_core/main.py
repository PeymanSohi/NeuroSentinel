from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "ML Core is running."}

@app.get("/health")
def health():
    return {"status": "ok"}

# Add endpoints for training, inference, etc. as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)