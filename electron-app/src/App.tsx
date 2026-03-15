import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Stars, Sparkles } from '@react-three/drei';
import * as random from 'maath/random/dist/maath-random.esm';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FolderInput, 
  Settings, 
  Zap, 
  Camera, 
  Monitor, 
  CheckCircle2, 
  RefreshCw,
  ChevronRight,
  Database,
  Globe,
  Cpu
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Utility ---
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- 3D Background Components ---

function ParticleField(props: any) {
  const ref = useRef<any>(null);
  const [sphere] = useState(() => {
      // @ts-ignore
      return random.inSphere(new Float32Array(5000), { radius: 1.5 });
  });
  
  useFrame((_state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10;
      ref.current.rotation.y -= delta / 15;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
        <PointMaterial
          transparent
          color="#a855f7" // Purple accent
          size={0.002}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={0.6}
        />
      </Points>
    </group>
  );
}

function Scene() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 1] }}>
        <fog attach="fog" args={['#000', 0.8, 2.5]} /> {/* Depth fog */}
        <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
          <ParticleField />
        </Float>
        <Sparkles count={100} scale={2} size={2} speed={0.4} opacity={0.3} color="#3b82f6" />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      </Canvas>
      {/* Cinematic Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#000_100%)] opacity-80" />
      <div className="absolute inset-0 cinematic-scan opacity-30" />
    </div>
  );
}

// --- UI Components ---

// 1. Holographic Status Bar
const HoloStatusBar = ({ devices }: { devices: any[] }) => {
  const photoDevice = devices.find(d => d.type === 'photo');
  const vrDevice = devices.find(d => d.type === 'vr');

  return (
    <motion.div 
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, type: "spring", stiffness: 200, damping: 20 }}
      className="h-14 mx-auto mt-6 bg-[#0a0a0a]/80 backdrop-blur-2xl border border-white/[0.08] rounded-full flex items-center px-8 gap-8 shadow-[0_8px_32px_rgba(0,0,0,0.5),0_0_0_1px_rgba(255,255,255,0.05)] z-50 drag-region w-fit min-w-[380px] justify-between relative overflow-hidden group hover:border-white/20 transition-all duration-500"
    >
      {/* Dynamic Glow Background */}
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 via-purple-500/5 to-indigo-500/5 opacity-50 group-hover:opacity-100 transition-opacity duration-700" />
      
      {/* Scanline effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-[shimmer_4s_infinite]" />
      
      {/* Left: Branding */}
      <div className="flex items-center gap-3 relative z-10 no-drag">
        <div className="relative flex items-center justify-center w-3 h-3">
          <div className="absolute inset-0 bg-indigo-500 rounded-full animate-ping opacity-75" />
          <div className="relative w-2 h-2 bg-indigo-400 rounded-full shadow-[0_0_8px_rgba(129,140,248,0.8)]" />
        </div>
        <span className="text-sm font-bold text-white tracking-[0.15em] shadow-black drop-shadow-lg">
          房勘工作流助手
        </span>
      </div>

      {/* Divider */}
      <div className="w-[1px] h-4 bg-white/10 relative z-10" />
      
      {/* Right: Status Indicators */}
      <div className="flex items-center gap-6 no-drag relative z-10">
        {/* Photo Status */}
        <div className="flex items-center gap-3 group/item">
          <div className={cn(
            "relative p-1.5 rounded-lg transition-all duration-300",
            photoDevice ? "bg-emerald-500/10 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]" : "text-gray-600"
          )}>
            <Camera size={16} className={cn("transition-transform duration-300", photoDevice && "group-hover/item:scale-110")} />
          </div>
          <div className="flex flex-col gap-0.5">
             <div className={cn("w-1.5 h-1.5 rounded-full transition-all duration-300", photoDevice ? "bg-emerald-500 shadow-[0_0_8px_#10b981]" : "bg-gray-700")} />
          </div>
        </div>

        {/* VR Status */}
        <div className="flex items-center gap-3 group/item">
          <div className={cn(
            "relative p-1.5 rounded-lg transition-all duration-300",
            vrDevice ? "bg-purple-500/10 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.2)]" : "text-gray-600"
          )}>
            <Monitor size={16} className={cn("transition-transform duration-300", vrDevice && "group-hover/item:scale-110")} />
          </div>
          <div className="flex flex-col gap-0.5">
             <div className={cn("w-1.5 h-1.5 rounded-full transition-all duration-300", vrDevice ? "bg-purple-500 shadow-[0_0_8px_#a855f7]" : "bg-gray-700")} />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// 2. Glassmorphism Card (Advanced)
const CyberCard = ({ children, className, delay = 0, glowColor = "rgba(255,255,255,0.03)" }: any) => {
    const [tilt, setTilt] = useState({ x: 0, y: 0 });
    const [glow, setGlow] = useState({ x: 50, y: 50, opacity: 0 });

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0, rotateX: tilt.x, rotateY: tilt.y }}
        whileHover={{ scale: 1.008 }}
        transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1], delay }}
        onMouseMove={(e) => {
          const rect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
          const px = (e.clientX - rect.left) / rect.width;
          const py = (e.clientY - rect.top) / rect.height;
          setTilt({ x: (0.5 - py) * 6, y: (px - 0.5) * 6 });
          setGlow({ x: px * 100, y: py * 100, opacity: 1 });
        }}
        onMouseLeave={() => {
          setTilt({ x: 0, y: 0 });
          setGlow({ x: 50, y: 50, opacity: 0 });
        }}
        className={cn(
          "relative overflow-hidden bg-[#0a0a0a]/60 backdrop-blur-xl border border-white/[0.08] shadow-2xl",
          "rounded-3xl group [transform-style:preserve-3d]",
          className
        )}
        style={{
          transformPerspective: 1400,
          boxShadow: `0 0 0 1px rgba(0,0,0,0.5), 0 4px 20px -2px rgba(0,0,0,0.5), inset 0 0 20px ${glowColor}`
        }}
      >
        <div
          className="absolute inset-0 pointer-events-none transition-opacity duration-300"
          style={{
            opacity: glow.opacity,
            background: `radial-gradient(260px circle at ${glow.x}% ${glow.y}%, rgba(129,140,248,0.18), transparent 60%)`
          }}
        />
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[size:20px_20px] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)]" />
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-white/[0.02] rounded-full blur-3xl pointer-events-none group-hover:bg-white/[0.05] transition-colors duration-700" />
        <motion.div
          className="absolute -left-20 top-1/2 w-40 h-[1px] bg-gradient-to-r from-transparent via-indigo-400/30 to-transparent pointer-events-none"
          animate={{ x: [-120, 520], opacity: [0, 0.6, 0] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: "linear", delay }}
        />
        <motion.div
          className="absolute inset-0 pointer-events-none"
          animate={{ opacity: [0.12, 0.22, 0.12] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay }}
          style={{
            background: "radial-gradient(42rem 20rem at 12% -8%, rgba(99,102,241,0.18), transparent 55%)"
          }}
        />
        <motion.div
          className="absolute inset-0 pointer-events-none"
          animate={{ opacity: [0.08, 0.18, 0.08] }}
          transition={{ duration: 6.2, repeat: Infinity, ease: "easeInOut", delay: delay + 0.3 }}
          style={{
            background: "radial-gradient(36rem 16rem at 88% 108%, rgba(56,189,248,0.16), transparent 60%)"
          }}
        />
        {children}
      </motion.div>
    );
};

// 3. Neon Action Button
const NeonButton = ({ onClick, label, subLabel, icon: Icon, color = "indigo", disabled }: any) => {
  const styles = {
    indigo: {
      orbit: "orbit-indigo",
      icon: "from-indigo-600 to-violet-600 shadow-[0_0_24px_rgba(99,102,241,0.38)]",
      sheen: "from-indigo-500/0 via-indigo-300/40 to-violet-500/0",
    },
    cyan: {
      orbit: "orbit-cyan",
      icon: "from-cyan-600 to-blue-600 shadow-[0_0_24px_rgba(6,182,212,0.38)]",
      sheen: "from-cyan-500/0 via-cyan-200/35 to-blue-500/0",
    },
  };
  const palette = styles[color as keyof typeof styles];

  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2, rotateX: 2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "group relative w-full rounded-2xl p-[1px] overflow-hidden transition-all duration-300 [transform-style:preserve-3d]",
        disabled && "opacity-50 grayscale cursor-not-allowed"
      )}
    >
      <div className={cn("absolute inset-0 pointer-events-none", palette.orbit)}>
        <div className="absolute inset-[-42%] orbit-core" />
      </div>

      <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
        <div className={cn("absolute inset-y-0 -left-1/3 w-1/2 bg-gradient-to-r blur-md opacity-70 group-hover:opacity-100 transition-opacity duration-500 orbit-sheen", palette.sheen)} />
      </div>

      <div className="relative h-full bg-[#080808] backdrop-blur-xl rounded-[15px] p-4 flex items-center justify-between z-10 group-hover:bg-[#0a0a0a] transition-colors border border-white/5 shadow-inner [transform-style:preserve-3d]">
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.14),transparent_45%)]" />
        <div className="absolute inset-0 opacity-40 pointer-events-none bg-[radial-gradient(140%_90%_at_50%_-30%,rgba(255,255,255,0.22),transparent_52%)]" />
        <div className="flex items-center gap-4">
          <div className={cn("p-3 rounded-xl bg-gradient-to-br text-white shadow-lg border border-white/10 relative overflow-hidden", palette.icon)}>
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
            <Icon size={20} className="drop-shadow-md relative z-10" />
          </div>
          <div className="text-left">
            <div className="text-sm font-bold text-white tracking-wide group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-300 transition-all">
              {label}
            </div>
            <div className="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5">{subLabel}</div>
          </div>
        </div>
        
        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors border border-white/5 group-hover:border-white/20 shadow-lg">
          <ChevronRight size={14} className="text-gray-500 group-hover:text-white transition-colors group-hover:translate-x-0.5 transform duration-300" />
        </div>
      </div>
    </motion.button>
  );
};

// 4. Data Stream Progress
const DataStreamProgress = ({ value, label, speed, color = "bg-indigo-500" }: any) => (
  <div className="space-y-1.5">
    <div className="flex justify-between items-center px-1">
      <div className="flex items-center gap-2">
        <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse shadow-glow", color.replace('bg-', 'text-'))} />
        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{label}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-[10px] font-mono text-gray-500 flex items-center gap-1">
           <Zap size={8} className="text-yellow-500" />
           {speed || "0 MB/s"}
        </span>
        <span className="text-[10px] font-mono text-white/90 tabular-nums bg-white/10 px-1.5 py-0.5 rounded text-center min-w-[3rem]">
            {value >= 100 ? "完成" : `${Math.min(100, value).toFixed(1)}%`}
        </span>
      </div>
    </div>
    
    <div className="h-2 bg-[#111] rounded-full overflow-hidden relative border border-white/5 shadow-inner">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        transition={{ type: "spring", stiffness: 50, damping: 15 }}
        className={cn("h-full rounded-full relative shadow-[0_0_10px_currentColor]", color)}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent w-full animate-[shimmer-fast_1.5s_infinite]" />
      </motion.div>
      <motion.div
        className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_12px_rgba(255,255,255,0.9)]"
        animate={{ left: `calc(${Math.min(100, value)}% - 5px)` }}
        transition={{ type: "spring", stiffness: 70, damping: 18 }}
      />
      
      {/* Data bits effect - refined */}
      <div className="absolute inset-0 flex justify-between px-0.5 opacity-30 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="w-[1px] h-full bg-black/50" />
        ))}
      </div>
    </div>
  </div>
);

// 5. Retro Sci-Fi Text Editor
const RetroEditor = ({ value, onChange, placeholder }: any) => (
  <div className="relative w-full h-full group starwars-frame">
    <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.04] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(56,189,248,0.06),rgba(129,140,248,0.02),rgba(34,211,238,0.06))]" style={{ backgroundSize: "100% 2px, 3px 100%" }} />
    <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden opacity-15">
       <div className="w-full h-[2px] bg-cyan-400/30 shadow-[0_0_12px_rgba(34,211,238,0.55)] animate-[scanline-vertical_8s_linear_infinite]" />
    </div>
    <div className="absolute inset-0 starwars-grid pointer-events-none z-0" />
    <div className="absolute inset-0 bg-cyan-500/5 blur-3xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-700 pointer-events-none" />

    <div className="absolute top-2 left-3 right-3 z-20 flex items-center justify-between pointer-events-none">
      <span className="hud-code text-[9px] text-cyan-300/70">NAVI-COMM // INPUT_CHANNEL</span>
      <span className="hud-code text-[9px] text-cyan-300/70">AUTH:PHOTOGRAPHER</span>
    </div>

    <textarea
      autoFocus
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full h-full bg-transparent pt-8 pb-8 px-6 text-sm leading-relaxed text-cyan-100/90 resize-none focus:outline-none placeholder-cyan-500/35 retro-text starwars-console relative z-10 selection:bg-cyan-500/40 selection:text-white"
      spellCheck={false}
      style={{
        textShadow: "0 0 7px rgba(34,211,238,0.45)"
      }}
    />

    <div className="absolute bottom-2 left-3 right-3 z-20 flex items-center justify-between pointer-events-none">
      <span className="hud-code text-[9px] text-cyan-300/55">SECTOR: CN-CHANGSHA</span>
      <span className="hud-code text-[9px] text-cyan-300/55">LINK_STABLE</span>
    </div>

    <div className="absolute top-0 left-0 w-5 h-5 border-l-2 border-t-2 border-cyan-400/45 rounded-tl-lg pointer-events-none hud-bracket" />
    <div className="absolute top-0 right-0 w-5 h-5 border-r-2 border-t-2 border-cyan-400/45 rounded-tr-lg pointer-events-none hud-bracket" />
    <div className="absolute bottom-0 left-0 w-5 h-5 border-l-2 border-b-2 border-cyan-400/45 rounded-bl-lg pointer-events-none hud-bracket" />
    <div className="absolute bottom-0 right-0 w-5 h-5 border-r-2 border-b-2 border-cyan-400/45 rounded-br-lg pointer-events-none hud-bracket" />
  </div>
);

function App() {
  const electron = (window as any).electron;
  const [inputText, setInputText] = useState("");
  const [stats, setStats] = useState({ count: 0, revenue: 0 });
  const [devices, setDevices] = useState<any[]>([]);
  const [importing, setImporting] = useState(false);
  const [progress, setProgress] = useState({ photo: { val: 0, speed: '' }, vr: { val: 0, speed: '' } });
  const [rootPath, setRootPath] = useState("~/Pictures");
  const [sceneEnabled, setSceneEnabled] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setSceneEnabled(true), 180);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    const lines = inputText.split('\n').filter(l => l.trim().length > 0);
    const count = lines.length;
    // Animate revenue counting up
    const targetRev = count * 28;
    
    setStats(prev => ({ ...prev, count }));
    
    // Simple lerp animation for revenue
    const interval = setInterval(() => {
        setStats(prev => {
            const diff = targetRev - prev.revenue;
            if (Math.abs(diff) < 1) return { ...prev, revenue: targetRev };
            return { ...prev, revenue: prev.revenue + Math.ceil(diff * 0.2) };
        });
    }, 50);
    
    return () => clearInterval(interval);
  }, [inputText]);

  // Initial Load
  const [photographer, setPhotographer] = useState("郭艳");

  useEffect(() => {
    if (!electron) return;
    electron.getSettings().then((s: any) => {
      if (s.root_dir) setRootPath(s.root_dir);
      if (s.photographer_name) setPhotographer(s.photographer_name);
    });
    
    const interval = setInterval(async () => {
        const devs = await electron.scanDevices();
        setDevices(devs);
    }, 2000);
    
    return () => clearInterval(interval);
  }, [electron]);

  const handlePhotographerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setPhotographer(val);
      if (electron) electron.saveSettings({ photographer_name: val });
  };

  // Progress Listener
  useEffect(() => {
      if (!electron) return;
      const cleanup = electron.onImportProgress((data: any) => {
          setProgress(prev => ({
              ...prev,
              [data.type]: {
                  val: (data.current / data.total) * 100,
                  speed: data.speed
              }
          }));
      });
      return cleanup;
  }, [electron]);

  const handleImport = async () => {
    if (!electron) return;
    setImporting(true);
    setProgress({ photo: { val: 0, speed: '0 MB/s' }, vr: { val: 0, speed: '0 MB/s' } });
    
    // Start both concurrently
    await Promise.all([
        electron.startImport({ type: 'photo' }),
        electron.startImport({ type: 'vr' })
    ]);
    
    // Force 100% completion state
    setProgress(prev => ({
        photo: { ...prev.photo, val: 100 },
        vr: { ...prev.vr, val: 100 }
    }));
    // Keep importing state true to show the completion UI
  };

  const handleCreateFolders = async () => {
      if (!electron) return;
      if (!inputText.trim()) return;
      const res = await electron.createFolders({ text: inputText });
      if (res.success) {
          alert(`成功创建 ${res.created} 个文件夹!\nExcel 新增记录: ${res.excel.added}`);
      } else {
          alert(`发生错误:\n${res.errors.join('\n')}`);
      }
  };

  const handleSelectRoot = async () => {
      if (!electron) return;
      const path = await electron.selectDirectory();
      if (path) {
          setRootPath(path);
          electron.saveSettings({ root_dir: path });
      }
  };

  const handleConfigSrc = async (type: 'photo' | 'vr') => {
      if (!electron) return;
      const path = await electron.selectDirectory();
      if (path) {
          if (type === 'photo') {
              electron.saveSettings({ photo_src: path });
          } else {
              electron.saveSettings({ vr_src: path });
          }
          const devs = await electron.scanDevices();
          setDevices(devs);
      }
  };

  const handleOpenFolder = async (type: 'photo' | 'vr') => {
      if (!electron) return;
      const device = type === 'photo' ? photoDevice : vrDevice;
      if (device && device.path) {
          await electron.openPath(device.path);
      } else {
          handleConfigSrc(type);
      }
  };

  const photoDevice = devices.find(d => d.type === 'photo');
  const vrDevice = devices.find(d => d.type === 'vr');

  return (
    <div className="h-screen bg-black text-white font-sans selection:bg-indigo-500/30 overflow-hidden relative flex flex-col">
      
      {/* 3D Background Scene */}
      {sceneEnabled ? <Scene /> : null}
      <div className="absolute inset-0 z-[1] pointer-events-none aurora-drift" />
      <div className="absolute inset-0 z-[2] pointer-events-none star-streaks" />
      <div className="absolute inset-0 z-[3] pointer-events-none volumetric-rays" />
      <div className="absolute inset-0 z-[4] pointer-events-none warp-vignette" />
      <div className="noise-bg" />

      {/* Global Drag Region (Title Bar) */}
      <div className="fixed top-0 left-0 w-full h-20 z-40 drag-region" />

      {/* Holographic Status Bar */}
      <HoloStatusBar devices={devices} />

      {/* Main Layout */}
      <div className="relative z-10 flex-1 max-w-[1600px] w-full mx-auto p-6 pb-8 grid grid-cols-12 gap-6 min-h-0">
        
        {/* Left: Cyberpunk Editor */}
        <div className="col-span-8 flex flex-col h-full">
          <CyberCard className="flex-1 flex flex-col min-h-0" delay={0.2} glowColor="rgba(99,102,241,0.05)">
            {/* Header */}
            <div className="h-10 border-b border-white/5 flex items-center justify-between px-4 bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <Database size={14} className="text-indigo-400" />
                <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">房源信息录入</span>
              </div>
              <div className="flex gap-3">
                 <button onClick={() => setInputText("")} className="text-[10px] font-bold uppercase tracking-wider text-gray-500 hover:text-white transition-colors px-2 py-1 rounded-lg border border-white/5 hover:border-white/20 hover:bg-white/5">清空</button>
              </div>
            </div>

            {/* Editor */}
            <div className="flex-1 relative group grid-bg">
              <RetroEditor 
                value={inputText}
                onChange={(e: any) => setInputText(e.target.value)}
                placeholder="// 请在此粘贴房源信息..."
              />
            </div>

            {/* Stats Bar */}
            <div className="h-10 border-t border-white/5 flex items-center justify-between px-4 bg-black/40 backdrop-blur-md">
              <div className="flex gap-4 text-xs font-mono text-gray-500 uppercase">
                <span className="flex items-center gap-2"><div className="w-1 h-1 bg-emerald-500 rounded-full" /> 系统就绪</span>
                <span className="flex items-center gap-2"><div className="w-1 h-1 bg-indigo-500 rounded-full" /> UTF-8 编码</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-xs text-gray-400 font-mono">
                  行数: <span className="text-white">{stats.count}</span>
                </div>
                <div className="h-3 w-[1px] bg-white/10" />
                <div className="text-xs font-bold text-indigo-400 font-mono">
                  预计收入: ¥{stats.revenue}
                </div>
              </div>
            </div>
          </CyberCard>
        </div>

        {/* Right: Command Module */}
        <div className="col-span-4 flex flex-col gap-6 h-full">
          
          {/* System Monitor */}
          <CyberCard className="p-5 bg-gradient-to-b from-[#111] to-black border-white/10" delay={0.3} glowColor="rgba(16,185,129,0.05)">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-[0.2em] flex items-center gap-2">
                <Cpu size={14} className="text-indigo-500" /> 硬件连接状态
              </h3>
              {/* Animated Signal Bars */}
              <div className="flex gap-1 items-end h-3">
                {[...Array(5)].map((_, i) => (
                  <motion.div 
                    key={i} 
                    initial={{ height: "40%" }}
                    animate={{ height: ["40%", "100%", "40%"] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.1, ease: "easeInOut" }}
                    className={cn(
                        "w-1 rounded-[1px]", 
                        i < 4 ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-gray-800"
                    )} 
                  />
                ))}
              </div>
            </div>

            <div className="space-y-3">
              {/* Photo Device Card */}
              <motion.div 
                whileHover={{ scale: 1.02, y: -2, rotateX: 2, rotateY: -2 }}
                className={cn(
                    "relative p-3 rounded-xl border overflow-hidden group cursor-pointer transition-all duration-300",
                    "bg-gradient-to-br from-[#1a1a1a] to-black",
                    photoDevice ? "border-indigo-500/30 shadow-[0_0_20px_rgba(79,70,229,0.15)]" : "border-white/5 hover:border-white/10"
                )}
                style={{ transformPerspective: 1200 }}
              >
                {/* Click Handler Overlay */}
                <div className="absolute inset-0 z-0" onClick={() => handleOpenFolder('photo')} />

                {/* Config Button (Only visible on hover or if not connected) */}
                <div 
                    className="absolute top-2 right-2 z-20 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-gray-400 hover:text-white cursor-pointer"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleConfigSrc('photo');
                    }}
                >
                    <Settings size={12} />
                </div>

                <div className="flex items-center gap-4 relative z-10 pointer-events-none">
                   {/* Icon Container with Glow */}
                   <div className={cn(
                       "w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-500 relative overflow-hidden",
                       photoDevice ? "bg-indigo-500/20 text-indigo-400" : "bg-white/5 text-gray-600"
                   )}>
                     {photoDevice && <div className="absolute inset-0 bg-indigo-500/20 blur-md" />}
                     <Camera size={20} className="relative z-10 drop-shadow-md" />
                   </div>
                   
                   <div className="flex-1">
                     <div className="flex items-center justify-between">
                        <div className="text-xs font-bold text-gray-100 tracking-wide">{photoDevice?.model || "相片源 (点击配置)"}</div>
                        {photoDevice && <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_#6366f1]" />}
                     </div>
                     <div className="text-[10px] font-mono text-gray-500 mt-0.5 flex items-center gap-2">
                        <span className={photoDevice ? "text-emerald-400" : "text-gray-600"}>{photoDevice ? '● 已连接' : '○ 未连接'}</span>
                        <span className="text-gray-700">::</span>
                        <span>{photoDevice ? '就绪' : '点击配置'}</span>
                     </div>
                   </div>
                </div>
                
                {/* Background scanning line */}
                {photoDevice && (
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-indigo-500/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite] pointer-events-none" />
                )}
              </motion.div>

              {/* VR Device Card */}
              <motion.div 
                whileHover={{ scale: 1.02, y: -2, rotateX: 2, rotateY: -2 }}
                className={cn(
                    "relative p-3 rounded-xl border overflow-hidden group cursor-pointer transition-all duration-300",
                    "bg-gradient-to-br from-[#1a1a1a] to-black",
                    vrDevice ? "border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.15)]" : "border-white/5 hover:border-white/10"
                )}
                style={{ transformPerspective: 1200 }}
              >
                {/* Click Handler Overlay */}
                <div className="absolute inset-0 z-0" onClick={() => handleOpenFolder('vr')} />

                {/* Config Button */}
                <div 
                    className="absolute top-2 right-2 z-20 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-gray-400 hover:text-white cursor-pointer"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleConfigSrc('vr');
                    }}
                >
                    <Settings size={12} />
                </div>

                <div className="flex items-center gap-4 relative z-10 pointer-events-none">
                   {/* Icon Container with Glow */}
                   <div className={cn(
                       "w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-500 relative overflow-hidden",
                       vrDevice ? "bg-purple-500/20 text-purple-400" : "bg-white/5 text-gray-600"
                   )}>
                     {vrDevice && <div className="absolute inset-0 bg-purple-500/20 blur-md" />}
                     <Globe size={20} className="relative z-10 drop-shadow-md" />
                   </div>
                   
                   <div className="flex-1">
                     <div className="flex items-center justify-between">
                        <div className="text-xs font-bold text-gray-100 tracking-wide">{vrDevice?.model || "全景源 (点击配置)"}</div>
                        {vrDevice && <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse shadow-[0_0_8px_#a855f7]" />}
                     </div>
                     <div className="text-[10px] font-mono text-gray-500 mt-0.5 flex items-center gap-2">
                        <span className={vrDevice ? "text-emerald-400" : "text-gray-600"}>{vrDevice ? '● 已连接' : '○ 未连接'}</span>
                        <span className="text-gray-700">::</span>
                        <span>{vrDevice ? '就绪' : '点击配置'}</span>
                     </div>
                   </div>
                </div>
                
                {vrDevice && (
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite] pointer-events-none" />
                )}
              </motion.div>
            </div>
          </CyberCard>

          <CyberCard className="flex-1 flex flex-col relative bg-black/40 min-h-0" delay={0.4} glowColor="rgba(168,85,247,0.05)">
            {/* Header */}
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] flex items-center gap-2 p-5 pb-2 sticky top-0 bg-black/0 backdrop-blur-sm z-20">
              <Zap size={12} /> 执行操作
            </h3>
            
            {/* Scrollable Content */}
            <div className="relative z-10 space-y-4 flex-1 overflow-y-auto px-5 custom-scrollbar min-h-0">
              <AnimatePresence mode="wait">
                {importing || true ? (
                  <motion.div
                    key="actions"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-4 pb-4"
                  >
                    <NeonButton 
                      label={importing && (progress.photo.val < 100 || progress.vr.val < 100) ? "正在导卡中..." : "开始并发导卡"} 
                      subLabel="自动检测并同步所有媒体"
                      icon={Zap} 
                      color="indigo"
                      onClick={handleImport}
                      disabled={importing && (progress.photo.val < 100 || progress.vr.val < 100)}
                    />
                    <NeonButton 
                      label="生成目录结构" 
                      subLabel="根据文本生成文件夹和 Excel"
                      icon={FolderInput} 
                      color="cyan"
                      onClick={handleCreateFolders}
                    />

                    {/* Progress Area */}
                    <div className={cn(
                        "transition-all duration-500 ease-in-out overflow-hidden",
                        importing ? "opacity-100 max-h-40 mb-4" : "opacity-0 max-h-0 mb-0"
                    )}>
                        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
                             <div className="flex items-center gap-2 mb-2">
                                {progress.photo.val >= 100 && progress.vr.val >= 100 ? (
                                    <CheckCircle2 className="text-emerald-400" size={14}/>
                                ) : (
                                    <RefreshCw className="animate-spin text-indigo-400" size={14}/>
                                )}
                                <span className="text-xs font-bold text-indigo-300">
                                    {progress.photo.val >= 100 && progress.vr.val >= 100 ? "同步完成" : "正在同步..."}
                                </span>
                             </div>
                             <DataStreamProgress value={progress.photo.val} speed={progress.photo.speed} label="相片" color="bg-indigo-500" />
                             <div className="h-2" />
                             <DataStreamProgress value={progress.vr.val} speed={progress.vr.speed} label="VR" color="bg-purple-500" />
                        </div>
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </div>

            {/* Footer - Fixed at bottom */}
            <div className="p-4 pt-3 border-t border-white/5 bg-black/40 backdrop-blur-md z-30 space-y-2 mt-auto">
              {/* Compact Footer Layout */}
              
              {/* Row 1: Photographer Input */}
              <div className="flex items-center justify-between gap-3 group">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider whitespace-nowrap group-hover:text-gray-400 transition-colors">
                  摄影档案名
                </span>
                <div className="flex-1 h-7 rounded-lg bg-black/40 border border-white/5 flex items-center px-2 transition-all hover:border-white/20 hover:bg-black/60 focus-within:border-indigo-500/30 focus-within:bg-indigo-500/5">
                  <input 
                    type="text" 
                    value={photographer}
                    onChange={handlePhotographerChange}
                    className="bg-transparent w-full text-xs font-mono text-gray-300 outline-none placeholder-gray-700 text-right focus:text-indigo-200 transition-colors"
                    placeholder="输入姓名..."
                  />
                </div>
              </div>

              {/* Row 2: Root Path Input */}
              <div className="flex items-center justify-between gap-3 group">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider whitespace-nowrap group-hover:text-gray-400 transition-colors">
                  目录路径
                </span>
                
                <div className="flex-1 flex items-center gap-2 min-w-0 justify-end">
                   {/* Path Display */}
                   <div 
                      className="flex-1 h-7 rounded-lg bg-black/40 border border-white/5 flex items-center px-2 min-w-0 transition-all hover:border-white/20 hover:bg-black/60"
                      title={rootPath}
                   >
                     <span className="text-[10px] font-mono text-gray-400 truncate w-full text-right dir-rtl">
                       {rootPath}
                     </span>
                   </div>
                   
                   {/* Config Button */}
                   <button 
                       onClick={handleSelectRoot}
                       className="h-7 w-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 hover:bg-indigo-500/20 hover:text-indigo-300 transition-all active:scale-95"
                       title="选择目录"
                   >
                     <Settings size={12} />
                   </button>
                </div>
              </div>
            </div>
          </CyberCard>

        </div>
      </div>
    </div>
  );
}

export default App;
