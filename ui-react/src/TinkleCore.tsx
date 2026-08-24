import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * TinkleCore — nested ring / holographic sphere visual.
 * Drop-in replacement for the placeholder <TinkleCore/> in main.tsx.
 *
 * Usage:
 *   <Canvas camera={{ position: [0, 0, 7], fov: 42 }}>
 *     <TinkleCore mode={mode} />
 *   </Canvas>
 */

type Mode = 'READY' | 'LISTENING' | 'SPEAKING' | 'EXECUTING' | 'EXPLAINING';

const CYAN = new THREE.Color('#5CFFF0');
const CYAN_DIM = new THREE.Color('#0FE3D6');

function useSoftDotTexture() {
  return useMemo(() => {
    const c = document.createElement('canvas');
    c.width = c.height = 64;
    const ctx = c.getContext('2d')!;
    const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.35, 'rgba(150,255,245,0.9)');
    g.addColorStop(1, 'rgba(150,255,245,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  }, []);
}

function RingShell({
  radius, band, count, speed, tilt, opacity, dotTex,
}: {
  radius: number; band: number; count: number; speed: number; tilt: number; opacity: number; dotTex: THREE.Texture;
}) {
  const ref = useRef<THREE.Points>(null!);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const lon = Math.random() * Math.PI * 2;
      const lat = (Math.random() * 2 - 1) * band;
      const r = radius * (0.985 + Math.random() * 0.03); // soft radial jitter -> no hard edge
      arr[i * 3] = r * Math.cos(lat) * Math.cos(lon);
      arr[i * 3 + 1] = r * Math.sin(lat);
      arr[i * 3 + 2] = r * Math.cos(lat) * Math.sin(lon);
    }
    return arr;
  }, [radius, band, count]);

  useFrame(() => {
    ref.current.rotation.y += speed;
  });

  return (
    <points ref={ref} rotation={[tilt, 0, 0]}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.028}
        map={dotTex}
        color={CYAN}
        transparent
        opacity={opacity}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        sizeAttenuation
      />
    </points>
  );
}

export function TinkleCore({ mode = 'READY' as Mode }: { mode?: Mode }) {
  const dotTex = useSoftDotTexture();
  const core = useRef<THREE.Mesh>(null!);
  const glow = useRef<THREE.Mesh>(null!);
  const t = useRef(0);

  const intensity = mode === 'EXECUTING' ? 1.5 : mode === 'SPEAKING' ? 1.2 : 1;

  useFrame((_, delta) => {
    t.current += delta;
    core.current.rotation.y -= 0.006 * intensity;
    core.current.rotation.x += 0.003;
    const s = 1 + Math.sin(t.current * 1.4) * 0.03;
    glow.current.scale.setScalar(s);
  });

  return (
    <group>
      <RingShell radius={2.55} band={0.62} count={5200} speed={0.018} tilt={0.05} opacity={0.55} dotTex={dotTex} />
      <RingShell radius={2.15} band={0.55} count={6400} speed={-0.014} tilt={-0.08} opacity={0.7} dotTex={dotTex} />
      <RingShell radius={1.72} band={0.48} count={5600} speed={0.02} tilt={0.12} opacity={0.8} dotTex={dotTex} />
      <RingShell radius={1.28} band={0.4} count={4200} speed={-0.024} tilt={-0.1} opacity={0.9} dotTex={dotTex} />

      {/* inner geodesic core — rounded facets, soft emissive, never hard-edged */}
      <mesh ref={core}>
        <icosahedronGeometry args={[0.62, 3]} />
        <meshBasicMaterial color={CYAN_DIM} wireframe transparent opacity={0.5} />
      </mesh>
      <mesh ref={glow}>
        <sphereGeometry args={[0.6, 48, 48]} />
        <meshBasicMaterial color={CYAN} transparent opacity={0.06} />
      </mesh>
    </group>
  );
}

export default TinkleCore;
