import { useState, useRef } from "react";
import { uploadZipFile } from "../services/api";
import { CloudArrowUpIcon, DocumentCheckIcon, ExclamationCircleIcon } from "@heroicons/react/24/outline"; // Assuming we want an icon, wait, I don't know if heroicons is installed. I will use SVG directly to be safe.

export default function UploadZone({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError("");
    if (!selectedFile.name.endsWith(".zip")) {
      setError("Por favor, selecciona un archivo .zip que contenga la tomografía DICOM.");
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError("");

    try {
      const response = await uploadZipFile(file);
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      console.error(err);
      setError("Error al conectar con el servidor. Verifica que FastAPI esté corriendo.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-panel w-full max-w-2xl mx-auto p-8 flex flex-col gap-8 animate-float">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
          Análisis de Tomografía
        </h2>
        <p className="text-slate-400">
          Sube tus archivos DICOM en formato .zip para generar una reconstrucción 3D y cortes 2D con IA.
        </p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ease-in-out flex flex-col items-center justify-center min-h-[250px] group ${
          isDragging 
            ? "border-primary bg-primary/10 scale-[1.02]" 
            : file 
              ? "border-secondary/50 bg-secondary/5 hover:bg-secondary/10" 
              : "border-slate-600 hover:border-primary/50 hover:bg-slate-800/50"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input
          type="file"
          accept=".zip"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />

        {file ? (
          <div className="flex flex-col items-center gap-4 animate-in fade-in zoom-in duration-300">
            <div className="p-4 bg-secondary/20 rounded-full text-secondary">
              <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="space-y-1">
              <p className="text-slate-300">Archivo listo para analizar</p>
              <p className="text-xl font-semibold text-secondary">{file.name}</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 text-slate-400 group-hover:text-slate-300 transition-colors">
            <div className={`p-4 rounded-full transition-colors duration-300 ${isDragging ? 'bg-primary/20 text-primary' : 'bg-slate-800'}`}>
              <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium">Arrastra y suelta tu archivo .zip aquí</p>
              <p className="text-sm text-slate-500 mt-1">o haz clic para explorar tus archivos</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl animate-in fade-in slide-in-from-top-2">
          <svg className="w-6 h-6 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
        className="btn-primary w-full text-lg relative overflow-hidden group"
      >
        <span className={`flex items-center justify-center gap-2 transition-transform duration-300 ${isUploading ? '-translate-y-12' : 'translate-y-0'}`}>
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Iniciar Análisis
        </span>
        <span className={`absolute inset-0 flex items-center justify-center gap-3 transition-transform duration-300 ${isUploading ? 'translate-y-0' : 'translate-y-12'}`}>
          <svg className="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Procesando modelo...
        </span>
      </button>
    </div>
  );
}
