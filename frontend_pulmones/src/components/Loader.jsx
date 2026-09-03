export default function Loader() {
  return (
    <div className="glass-panel p-12 flex flex-col items-center justify-center w-full max-w-lg mx-auto min-h-[400px] text-center space-y-6">
      <div className="relative">
        {/* Outer rotating ring */}
        <div className="absolute inset-0 rounded-full border-t-2 border-primary border-r-2 border-transparent animate-spin w-24 h-24 mx-auto -m-4"></div>
        {/* Inner static/pulsing core */}
        <div className="bg-primary/20 p-4 rounded-full animate-pulse-slow">
          <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
      </div>
      
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-wide">
          Procesando Tomografía
        </h2>
        <p className="text-slate-400 max-w-[280px] leading-relaxed mx-auto">
          La inteligencia artificial está analizando los cortes DICOM y generando la reconstrucción 3D.
        </p>
      </div>

      <div className="w-full bg-slate-800 rounded-full h-1.5 mt-4 overflow-hidden">
        <div className="bg-primary h-1.5 rounded-full w-full animate-[progress_2s_ease-in-out_infinite] origin-left"></div>
      </div>
    </div>
  );
}