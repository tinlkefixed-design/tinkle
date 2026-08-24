declare module 'react' { export type ReactNode = unknown; export function useState<T>(x:T):[T,(v:T)=>void]; export function useMemo<T>(f:()=>T,d:any[]):T; export function useRef<T>(x:T):{current:T}; export function useEffect(f:()=>void|(()=>void),d?:any[]):void; export function createElement(...args:any[]):any; }
declare module 'react/jsx-runtime' { export function jsx(...args:any[]):any; export function jsxs(...args:any[]):any; export const Fragment:any; }
declare module 'react-dom/client' { export function createRoot(el:Element):{render(x:any):void}; }
declare module 'three' { export class Scene{} export class PerspectiveCamera{} export class WebGLRenderer{} export class Object3D{} }
declare module '@react-three/fiber' { export const Canvas:any; export function useFrame(...args:any[]):void; }
declare namespace JSX { interface IntrinsicElements { main:any; header:any; nav:any; button:any; mesh:any; sphereGeometry:any; meshStandardMaterial:any; ambientLight:any; } }
declare const document: any;
