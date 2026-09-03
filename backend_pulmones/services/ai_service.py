import os
import torch
from ai_model.architecture import get_model

# 1. Definimos la ruta al archivo que acabas de agregar
WEIGHTS_PATH = os.path.join("ai_model", "modelo_entrenado.pth")

# 2. Cargamos el modelo a la memoria (se hace aquí afuera para que 
# FastAPI lo cargue solo una vez al arrancar, y no en cada petición)
try:
    print("Cargando modelo de IA en memoria...")
    modelo_ia = get_model(WEIGHTS_PATH)
except Exception as e:
    print(f"Error crítico al cargar el modelo: {e}")
    modelo_ia = None

def run_inference(image_paths: list):
    """
    Función que usará el modelo cargado para analizar los PNGs.
    """
    if modelo_ia is None:
        return False, 0.0 # Fallback de seguridad si el modelo no cargó

    print(f"[AI Service] Analizando {len(image_paths)} cortes con la red neuronal...")
    
    # TODO: Aquí irá el bucle que convierte cada PNG a tensor y hace:
    # prediction = modelo_ia(image_tensor)
    
    # Simulación temporal del resultado final
    tumor_detected = True
    confidence = 94.5
    
    return tumor_detected, confidence