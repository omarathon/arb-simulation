import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.arb_executor.src.arb_executor import ArbExecutor
from backend.arb_executor.src.redis_listener import RedisListener

# Initialize ArbEngine and RedisListener
arb_executor = ArbExecutor()
redis_listener = RedisListener(arb_executor)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages startup and shutdown of background tasks."""
    task = asyncio.create_task(redis_listener.listen())

    print("🚀 Redis Listener started.")

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected on shutdown

        print("🛑 Redis Listener shut down.")

app = FastAPI(
    title="Arbitrage Executor API",
    description="API for execitomg arbitrage opportunities.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "OK"}
