import { useState } from "react";
import UploadZone from "../components/UploadZone";
import SliceViewer from '../components/SliceViewer';
import MeshViewer from '../components/MeshViewer';
import Loader from '../components/Loader';
import { checkTaskStatus } from '../services/api';

export default function Dashboard() {
  const [appState, setAppState] = useState("upload");
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleUploadSuccess = (responseData) => {
    setAppState("processing");
    const taskId = responseData.task_id;

    const intervalId = setInterval(async () => {
      try {
        const statusData = await checkTaskStatus(taskId);
        if (statusData.status === 'completed') {
          clearInterval(intervalId);
          setAnalysisResults(statusData.results);
          setAppState("results");
        } else if (statusData.status === 'not_found' || statusData.status === 'error') {
          console.error("Error en la tarea:", statusData.message);
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error("Error consultando estado:", error);
        clearInterval(intervalId);
      }
    }, 2000);
  };

  const handleReset = () => {
    setAppState("upload");
    setAnalysisResults(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
      <header className="bg-blue-900 text-white p-8 text-center shadow-md">
        <h1 className="text-3xl font-bold mb-2">Sistema de Análisis Pulmonar Asistido por IA</h1>
        <p className="text-blue-200">Sube un estudio DICOM comprimido en .zip para su evaluación</p>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        {appState === "upload" && (
          <UploadZone onUploadSuccess={handleUploadSuccess} />
        )}

        {appState === "processing" && (
          <Loader />
        )}

        {appState === "results" && analysisResults && (
          <div className="flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h2 className="text-2xl font-bold text-gray-700 mb-4 sm:mb-0">Resultados del Análisis</h2>
              <div className="flex items-center gap-4">
                <span className={`px-4 py-2 rounded-full font-bold text-sm ${
                  analysisResults.tumorDetected ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                }`}>
                  {analysisResults.tumorDetected ? 'Anomalía Detectada' : 'Sin Anomalías'}
                </span>
                <span className="text-gray-600 font-medium">
                  Confianza IA: {analysisResults.confidence}%
                </span>
                <button 
                  onClick={handleReset}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md font-medium transition-colors"
                >
                  Analizar otro
                </button>
              </div>
            </div>

            {/* Tarjeta de métricas y estadísticas clínicas */}
            {analysisResults.stats && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white p-5 rounded-lg shadow-sm border border-gray-100 text-center">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-semibold uppercase">Diámetro Estimado</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">{analysisResults.stats.diametroAprox}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-semibold uppercase">Área Máxima</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">{analysisResults.stats.areaAfectadaMax}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-semibold uppercase">Volumen Afectado</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">{analysisResults.stats.volumenEstimado}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-semibold uppercase">Cortes con Hallazgos</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">{analysisResults.stats.slicesAfectados}</p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col min-h-[500px]">
                <h3 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Visor 3D</h3>
                <div className="flex-1 bg-gray-900 rounded-md overflow-hidden relative">
                  <MeshViewer modelUrl={analysisResults.model3dUrl} />
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col min-h-[500px]">
                <h3 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Cortes 2D (Marcados)</h3>
                <div className="flex-1 bg-gray-900 rounded-md overflow-hidden">
                  <SliceViewer slices={analysisResults.slices2dUrls} />
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}