from fastapi import FastAPI
from uvicorn import run
from routes.api import api_router

app = FastAPI()

# Mount the entire “/api” subtree
app.include_router(api_router)

def main():
    run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
