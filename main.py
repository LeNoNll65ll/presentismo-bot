from fastapi import FastAPI
import asyncio
import logging
from scheduler import start_scheduler, client, scheduler
from listener import start_listener

logging.basicConfig(level=logging.INFO)
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Bot de presentismo iniciado")
    start_scheduler()
    asyncio.create_task(start_listener())

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()
    scheduler.shutdown()

@app.get("/")
def root():
    return {"status": "ok", "message": "Bot de presentismo corriendo"}

# main.py (agregá estos dos endpoints)
from scheduler import send_poll, generar_reporte, client, start_scheduler

@app.get("/send_poll_now")
async def send_poll_now():
    await send_poll()
    return {"ok": True}

@app.get("/report_now")
def report_now():
    generar_reporte()
    return {"ok": True}

# main.py (ya lo venías haciendo, confirmá que usa el client importado de scheduler)
@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()
    scheduler.shutdown()
