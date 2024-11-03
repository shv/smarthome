"""
Main
"""
import uvicorn
from fastapi import FastAPI

# Browser routers
from smarthome.routers.browser.front import router as browser_front_router
from smarthome.routers.browser.apis.auth import router as browser_apis_me_router
from smarthome.routers.browser.apis.nodes import router as browser_apis_nodes_router
from smarthome.routers.browser.ws.endpoints import router as browser_ws_router

# Nodes routers
from smarthome.routers.nodes.ws.endpoints import router as nodes_ws_router

# Other routers
from smarthome.routers.system.healthcheck import router as system_healthcheck_router

app = FastAPI()
app.include_router(browser_front_router)
app.include_router(browser_apis_me_router, prefix="/api/auth")
app.include_router(browser_apis_nodes_router, prefix="/api/nodes")
app.include_router(browser_ws_router)
app.include_router(nodes_ws_router)
app.include_router(system_healthcheck_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
