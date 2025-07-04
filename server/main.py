from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "NeuroSentinel API is running."}

@app.get("/health")
def health():
    # TODO: Add DB/Redis health checks
    return {"status": "ok"}
