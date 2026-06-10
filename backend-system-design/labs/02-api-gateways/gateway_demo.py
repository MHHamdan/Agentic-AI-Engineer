"""API gateway lab demonstration with a router and backend service simulation."""

from typing import List

import uvicorn
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Gateway Demo")

gateway_router = APIRouter(prefix="/gateway")
service_router = APIRouter(prefix="/internal")

class Item(BaseModel):
    """Represents an item returned by the internal service."""

    id: int
    name: str

service_items = [
    Item(id=1, name="Widget"),
    Item(id=2, name="Gadget"),
]

@service_router.get("/items", response_model=List[Item])
def list_internal_items():
    """Return the internal service item list."""
    return service_items

@gateway_router.get("/items", response_model=List[Item])
def gateway_list_items():
    """Forward a gateway request to the internal item list."""
    return list_internal_items()

@gateway_router.get("/status")
def gateway_status():
    """Return the gateway service status."""
    return {"gateway": "online", "backend": "internal service available"}

app.include_router(gateway_router)
app.include_router(service_router)

if __name__ == "__main__":
    uvicorn.run("gateway_demo:app", host="127.0.0.1", port=8000, reload=False)
