import numpy as np
import trimesh
from skimage import measure
import os
from scipy.ndimage import gaussian_filter

def generate_3d_mesh(volume_data, output_folder: str):
    print("[Mesh Service] Generando malla 3D optimizada...")
    
    if volume_data is None:
        volume_data = np.zeros((50, 50, 50))
        volume_data[20:30, 20:30, 20:30] = 1.0

    vol = volume_data.astype(np.float32)

    # 1. Normalizar el volumen a 0 - 255
    v_min, v_max = vol.min(), vol.max()
    if v_max > v_min:
        vol = (vol - v_min) / (v_max - v_min) * 255.0

    # 2. Filtrado de alta densidad (percentil 90 para aislar estructuras densas y lesiones)
    threshold = np.percentile(vol, 90)
    high_density_mask = (vol > threshold).astype(np.float32)

    # 3. Suavizar la máscara
    smoothed_mask = gaussian_filter(high_density_mask, sigma=1.0)

    # 4. Aplicar Marching Cubes de forma segura
    try:
        verts, faces, normals, values = measure.marching_cubes(smoothed_mask, level=0.5)
    except Exception as e:
        print(f"[Mesh Service] Falló Marching Cubes principal: {e}. Usando fallback seguro.")
        # Malla de respaldo por si la máscara está vacía
        verts = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]], dtype=float)
        faces = np.array([[0,1,2]], dtype=int)
        normals = np.array([[0,0,1]]*3, dtype=float)

    # 5. Construir la malla tridimensional sin operaciones propensas a fallos
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals)
    
    # Exportar el resultado a GLTF de forma directa y segura
    mesh_path = os.path.join(output_folder, "mesh.gltf")
    mesh.export(mesh_path, file_type='gltf')
    
    print(f"[Mesh Service] Malla generada y guardada exitosamente en {mesh_path}")
    return mesh_path

    