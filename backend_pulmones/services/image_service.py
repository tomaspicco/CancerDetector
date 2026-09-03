import os
import zipfile
import pydicom
import numpy as np
from PIL import Image

def process_tomography_zip(zip_path: str, output_folder: str):
    """
    Descomprime el ZIP, detecta si son archivos DICOM (.dcm) o PNGs,
    genera las imágenes normalizadas para el visor 2D y retorna
    el volumen 3D en formato numpy array para la malla.
    """
    extract_dir = os.path.join(output_folder, "extracted_data")
    os.makedirs(extract_dir, exist_ok=True)
    
    # 1. Descomprimir el archivo ZIP recibido
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
        
    dicom_files = []
    png_files = []
    
    # 2. Clasificar los archivos extraídos
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_lower = file.lower()
            full_path = os.path.join(root, file)
            if file_lower.endswith('.dcm') or '.' not in file:
                dicom_files.append(full_path)
            elif file_lower.endswith(('.png', '.jpg', '.jpeg')):
                png_files.append(full_path)

    slice_filenames = []
    volume_list = []

    # 3. Rama A: Si el ZIP contiene DICOMs reales
    if dicom_files:
        slices = []
        for f_path in dicom_files:
            try:
                ds = pydicom.dcmread(f_path)
                if hasattr(ds, 'pixel_array'):
                    slices.append(ds)
            except Exception as e:
                print(f"[Image Service] Error leyendo DICOM {f_path}: {e}")
                
        # Ordenar cortes por posición en el eje Z si está disponible
        try:
            slices.sort(key=lambda s: float(s.ImagePositionPatient[2]) if hasattr(s, 'ImagePositionPatient') else 0.0)
        except Exception:
            pass

        for i, ds in enumerate(slices):
            arr = ds.pixel_array.astype(np.float32)
            # Normalizar píxeles a rango 0-255 para visualización web
            if arr.max() > arr.min():
                arr = ((arr - arr.min()) / (arr.max() - arr.min())) * 255.0
            arr = arr.astype(np.uint8)
            
            # Guardar PNG exportado
            img = Image.fromarray(arr).convert('RGB')
            filename = f"slice_{i:03d}.png"
            img.save(os.path.join(output_folder, filename))
            slice_filenames.append(filename)
            
            volume_list.append(ds.pixel_array.astype(np.float32))

        volume_3d = np.stack(volume_list, axis=0) if volume_list else None
        return volume_3d, slice_filenames

    # 4. Rama B: Si el ZIP contiene los PNGs sintéticos de prueba
    elif png_files:
        png_files.sort()
        for i, f_path in enumerate(png_files):
            filename = f"slice_{i:03d}.png"
            dest_path = os.path.join(output_folder, filename)
            
            # Copiar y convertir a escala de grises para volumen 3D sintético
            img = Image.open(f_path).convert('L')
            img.save(dest_path)
            slice_filenames.append(filename)
            volume_list.append(np.array(img, dtype=np.float32))
            
        volume_3d = np.stack(volume_list, axis=0) if volume_list else None
        return volume_3d, slice_filenames

    return None, []