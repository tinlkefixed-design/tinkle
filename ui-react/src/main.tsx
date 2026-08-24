import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas } from '@react-three/fiber';
import { EffectComposer, Bloom } from '@react-three/postprocessing'; // npm i @react-three/postprocessing
import { TinkleCore } from './TinkleCore';
import './smooth-ui.css';

const modes = ['READY', 'LISTENING', 'SPEAKING', 'EXECUTING', 'EXPLAINING'] as const;
type Mode = typeof modes[number];

function App() {
  const [mode, setMode] = useState<Mode>('READY');
  const label = useMemo(() => `Tinkle • ${mode}`, [mode]);

  return (
    <main className="tinkle-shell">
      <header className="tinkle-header">{label}</header>

      <Canvas camera={{ position: [0, 0, 7], fov: 42 }}>
        <ambientLight intensity={0.4} />
        <TinkleCore mode={mode} />
        <EffectComposer>
          <Bloom intensity={1.1} luminanceThreshold={0.12} luminanceSmoothing={0.85} mipmapBlur />
        </EffectComposer>
      </Canvas>

      <nav className="tinkle-modes">
        {modes.map((m) => (
          <button key={m} className={`mode-btn ${m === mode ? 'active' : ''}`} onClick={() => setMode(m)}>
            {m}
          </button>
        ))}
      </nav>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
