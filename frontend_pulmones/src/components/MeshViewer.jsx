import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import {
  OrbitControls,
  Stage,
  useGLTF,
  Html,
  useProgress,
} from "@react-three/drei";

function LoaderFallback() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 rounded-full border-2 border-slate-700 border-t-primary animate-spin"></div>
        <div className="text-slate-300 font-medium whitespace-nowrap bg-slate-900/80 px-4 py-2 rounded-full backdrop-blur-sm">
          {progress.toFixed(0)}% Cargando Modelo
        </div>
      </div>
    </Html>
  );
}

function LungModel({ url }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export default function MeshViewer({ modelUrl }) {
  if (!modelUrl) return null;

  return (
    <div className="w-full h-full min-h-[400px] md:min-h-[500px] lg:min-h-[600px] rounded-2xl overflow-hidden shadow-2xl border border-slate-700/50 relative bg-[#121826]">
      {/* Decorative corners */}
      <div className="absolute top-4 left-4 w-4 h-4 border-t-2 border-l-2 border-primary/50 z-10"></div>
      <div className="absolute top-4 right-4 w-4 h-4 border-t-2 border-r-2 border-primary/50 z-10"></div>
      <div className="absolute bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-primary/50 z-10"></div>
      <div className="absolute bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-primary/50 z-10"></div>

      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-black/40 backdrop-blur-md px-4 py-1.5 rounded-full border border-white/10 text-xs font-mono text-primary/80 tracking-wider">
        3D RECONSTRUCTION
      </div>

      <Canvas dpr={[1, 2]} camera={{ fov: 45 }}>
        <color attach="background" args={["#121826"]} />
        <Suspense fallback={<LoaderFallback />}>
          <Stage environment="city" intensity={0.6} adjustCamera>
            <LungModel url={modelUrl} />
          </Stage>
        </Suspense>
        <OrbitControls autoRotate={true} autoRotateSpeed={0.5} enablePan={true} enableZoom={true} makeDefault />
      </Canvas>
    </div>
  );
}
