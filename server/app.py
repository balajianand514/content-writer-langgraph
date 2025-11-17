from fastapi import FastAPI, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from .api import api_router



# Initialize FastAPI app with middleware
app = FastAPI(
    title='DocumentProcessing',
    middleware=[
        Middleware(ServerErrorMiddleware),
        Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    ]
)
# app.state.limiter = slowapi_rate_limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API routes
# @app.get('/api/user/validate')
# async def validate_user(user: User = Depends(get_user_info)):
#     if not user.id:
#         return {'allowed': False, "code": 401, "data": {}}

#     for group in user.groups:
#         if SETTINGS.whitelisted_ad_group in group:
#             return {'allowed': True, "code": 200, "data": user.model_dump()}

#     return {'allowed': False, "code": 403, "data": {}}


@app.get('/api/health')
async def health_check():
    return {"status": "healthy"}

# Include additional API routes
app.include_router(api_router, prefix='/api/v1')