from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from services.image_service import process_tomography_zip
from services.mesh_service import generate_3d_mesh
from services.ai_service import run_inference

router = APIRouter()
UPLOAD_DIR = "temp_storage/uploads"
OUTPUT_DIR = "temp_storage/outputs"
tasks_db = {}

def process_workflow(task_id: str, file_path: str):
    tasks_db[task_id] = {"status": "processing"}
    print(f"[TAREA {task_id}] Iniciando pipeline de procesamiento...")
    
    task_output_folder = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(task_output_folder, exist_ok=True)
    
    try:
        # 1. Extraer ZIP y obtener volumen 3D y lista de cortes
        volume_3d, slice_filenames = process_tomography_zip(file_path, task_output_folder)
        
        # 2. Generar malla 3D GLTF usando Marching Cubes
        generate_3d_mesh(volume_3d, task_output_folder)
        
        # 3. Inferencia con la red neuronal y estadísticas
        slice_paths = [os.path.join(task_output_folder, f) for f in slice_filenames]
        tumor_detected, confidence, stats = run_inference(slice_paths)
        
        base_url = "http://localhost:8000/api/download"
        slices_urls = [f"{base_url}/{task_id}/{fname}" for fname in slice_filenames]
        
        tasks_db[task_id] = {
            "status": "completed",
            "results": {
                "tumorDetected": tumor_detected,
                "confidence": confidence,
                "stats": stats,
                "model3dUrl": f"{base_url}/{task_id}/mesh.gltf",
                "slices2dUrls": slices_urls
            }
        }
        print(f"[TAREA {task_id}] Pipeline completado exitosamente.")
        
    except Exception as e:
        print(f"[TAREA {task_id}] Error crítico durante el procesamiento: {e}")
        tasks_db[task_id] = {"status": "error", "message": str(e)}

@router.post("/upload")
async def upload_tomography(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}.{file_extension}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(process_workflow, task_id, file_path)
    return {
        "status": "success",
        "message": "Archivo recibido correctamente.",
        "task_id": task_id,
        "filename": file.filename
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        return {"status": "not_found"}
    return task

@router.get("/download/{task_id}/{filename}")
def download_result(task_id: str, filename: str):
    task_folder = os.path.join(OUTPUT_DIR, task_id)
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(task_folder, safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
        
    return FileResponse(file_path)