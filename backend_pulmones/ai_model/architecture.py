import torch
import torch.nn as nn

class LungTumorUNet(nn.Module):
    """
    Arquitectura base de una red U-Net simplificada para segmentación médica.
    Toma una imagen DICOM (1 canal, escala de grises) y devuelve una máscara
    resaltando las zonas donde detecta anomalías.
    """
    def __init__(self):
        super(LungTumorUNet, self).__init__()
        
        # --- ENCODER (Extrae características de la imagen) ---
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        # --- BOTTLENECK (Capa profunda) ---
        self.bottleneck = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )
        
        # --- DECODER (Reconstruye la imagen para crear la máscara) ---
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
            # Salida de 1 canal (blanco y negro) con Sigmoid para probabilidades entre 0 y 1
            nn.Conv2d(in_channels=64, out_channels=1, kernel_size=1),
            nn.Sigmoid() 
        )

    def forward(self, x):
        # Flujo de los datos a través de la red
        x1 = self.encoder(x)
        x2 = self.bottleneck(x1)
        out = self.decoder(x2)
        return out

def get_model(weights_path: str = None):
    """
    Función auxiliar que el `ai_service.py` llamará para instanciar el modelo
    y cargar los pesos entrenados (.pth) si existen.
    """
    model = LungTumorUNet()
    
    if weights_path:
        try:
            # map_location='cpu' asegura que funcione aunque el servidor no tenga tarjeta de video (GPU)
            model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
            print(f"Pesos cargados correctamente desde {weights_path}")
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los pesos. Error: {e}")
            
    # Ponemos el modelo en modo evaluación (no entrenamiento)
    model.eval() 
    return model