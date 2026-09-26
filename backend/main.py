from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from routes import router as chat_router
import uvicorn
import os


app = FastAPI()

app.include_router(chat_router)

    

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST"), port=os.getenv("PORT") )
