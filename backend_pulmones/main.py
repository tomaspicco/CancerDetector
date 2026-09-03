from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Importamos las rutas que creamos en api/routes.py
from api.routes import router

app = FastAPI(title="API Análisis Pulmonar con IA")

# Configuración de CORS para permitir que React se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, pon la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los endpoints bajo el prefijo /api
app.include_router(router, prefix="/api")

# Crear carpetas temporales automáticamente al iniciar el servidor
os.makedirs("temp_storage/uploads", exist_ok=True)
os.makedirs("temp_storage/outputs", exist_ok=True)