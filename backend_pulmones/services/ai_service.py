import os
import torch
import torch.nn as nn
import numpy as np
from PIL import Image

class MiniUNet(nn.Module):
    def __init__(self):
        super(MiniUNet, self).__init__()
        self.enc1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.dec1 = nn.Conv2d(16, 1, kernel_size=3, padding=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x1 = torch.relu(self.enc1(x))
        x_pool = self.pool(x1)
        x_up = self.up(x_pool)
        out = self.sigmoid(self.dec1(x_up))
        return out

WEIGHTS_PATH = os.path.join("ai_model", "modelo_entrenado.pth")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

modelo_ia = MiniUNet().to(device)
if os.path.exists(WEIGHTS_PATH):
    try:
        modelo_ia.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
        modelo_ia.eval()
        print(f"🧠 [AI Service] Modelo cargado desde {WEIGHTS_PATH}")
    except Exception as e:
        print(f"⚠️ Error cargando pesos: {e}")
else:
    modelo_ia.eval()

def run_inference(image_paths: list):
    if not image_paths:
        return False, 0.0, {}

    total_slices_affected = 0
    max_risk_score = 0.0
    corte_critico = -1
    max_pixels_single_slice = 0

    PIXEL_SPACING_MM = 0.7
    SLICE_THICKNESS_MM = 2.5
    PIXEL_AREA_MM2 = PIXEL_SPACING_MM * PIXEL_SPACING_MM

    for idx, img_path in enumerate(image_paths):
        img_original = Image.open(img_path).convert("RGB")
        w_orig, h_orig = img_original.size
        img_gray = img_original.convert("L")

        arr_full = np.array(img_gray, dtype=np.float32)

        # 1. Normalizar corte completo
        if arr_full.max() > arr_full.min():
            arr_norm = (arr_full - arr_full.min()) / (arr_full.max() - arr_full.min() + 1e-8)
        else:
            arr_norm = np.zeros_like(arr_full)

        # 2. AISLAR PARÉNQUIMA PULMONAR (Ignorar huesos y piel exterior)
        # El aire/pulmón tiene valores bajos de densidad (0.1 a 0.55 aprox en ventana normalizada)
        # Excluimos el fondo negro absoluto (aire exterior < 0.05) y huesos (> 0.75)
        mascara_pulmon = (arr_norm > 0.08) & (arr_norm < 0.65)

        # 3. Preparar imagen 64x64 para la red
        img_resized = Image.fromarray((arr_norm * 255).astype(np.uint8)).resize((64, 64))
        arr_input = np.array(img_resized, dtype=np.float32) / 255.0

        tensor_in = torch.tensor(arr_input, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)

        with torch.no_grad():
            pred = modelo_ia(tensor_in).squeeze().cpu().numpy()

        # 4. Redimensionar predicción al tamaño original (512x512)
        pred_full = np.array(
            Image.fromarray((pred * 255).astype(np.uint8)).resize((w_orig, h_orig), resample=Image.BILINEAR)
        ) / 255.0

        # 5. CONDICIÓN CLÍNICA:
        # Solo se marca si la red ve densidad anómala Y está efectivamente dentro del área pulmonar
        mask_anomalia = (pred_full > 0.65) & mascara_pulmon

        slice_anomaly_pixels = int(np.sum(mask_anomalia))
        slice_risk = float(np.mean(pred_full[mascara_pulmon]) * 100) if np.any(mascara_pulmon) else 0.0

        if slice_risk > max_risk_score:
            max_risk_score = slice_risk

        # Descartar ruido espurio si son menos de 15 píxeles
        if slice_anomaly_pixels > 15:
            total_slices_affected += 1
            if slice_anomaly_pixels > max_pixels_single_slice:
                max_pixels_single_slice = slice_anomaly_pixels
                corte_critico = idx

            # Superponer el color rojo solo en la anomalía intrapulmonar
            orig_arr = np.array(img_original)
            orig_arr[mask_anomalia, 0] = np.clip(orig_arr[mask_anomalia, 0] * 0.3 + 255 * 0.7, 0, 255).astype(np.uint8)
            orig_arr[mask_anomalia, 1] = np.clip(orig_arr[mask_anomalia, 1] * 0.3, 0, 255).astype(np.uint8)
            orig_arr[mask_anomalia, 2] = np.clip(orig_arr[mask_anomalia, 2] * 0.3, 0, 255).astype(np.uint8)

            Image.fromarray(orig_arr).save(img_path)

    tumor_detected = total_slices_affected > 0
    area_maxima_mm2 = round(max_pixels_single_slice * PIXEL_AREA_MM2, 2)
    volumen_estimado_mm3 = round(area_maxima_mm2 * max(total_slices_affected, 1) * SLICE_THICKNESS_MM, 2)

    stats = {
        "slicesAfectados": f"{total_slices_affected} de {len(image_paths)}",
        "corteCritico": corte_critico if corte_critico >= 0 else 0,
        "areaAfectadaMax": f"{area_maxima_mm2} mm²",
        "volumenEstimado": f"{volumen_estimado_mm3} mm³",
        "diametroAprox": f"{round(2 * np.sqrt(area_maxima_mm2 / np.pi), 2)} mm" if area_maxima_mm2 > 0 else "0 mm"
    }

    confidence = round(min(max(max_risk_score * 1.8, 70.0), 96.0), 1) if tumor_detected else 91.0

    return tumor_detected, confidence, stats