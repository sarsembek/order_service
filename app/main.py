from fastapi import FastAPI

app = FastAPI()

if __name__ == "main":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    