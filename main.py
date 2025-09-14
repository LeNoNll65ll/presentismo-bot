# main.py
import asyncio
import listener_db
import presentismo

async def main():
    # iniciar scheduler
    scheduler = presentismo.start_scheduler()

    try:
        # correr listener_db hasta que se corte
        await listener_db.main()
    finally:
        scheduler.shutdown()
        print("⏹ Scheduler detenido")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⏹ Bot detenido")
