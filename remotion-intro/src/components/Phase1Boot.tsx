import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Phase1Boot: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Glitch effect on opacity
  const opacity = interpolate(frame, [0, 2, 4, 6, 8, 10, 15], [0, 1, 0, 1, 0.5, 1, 1], {
    extrapolateRight: "clamp",
  });
  
  const scale = spring({
    frame,
    fps,
    config: { damping: 12 },
  });

  const logs = [
    "INIT NICO-ANALYZER v4.0.1...",
    "ALLOCATING MEMORY BLOCKS [OK]",
    "LOADING characters.csv... [SUCCESS]",
    "CONNECTING DB... [OK]",
    "ESTABLISHING NEURAL LINK... [OK]",
    "SYSTEM READY."
  ];

  const visibleLogs = Math.floor(interpolate(frame, [10, 45], [0, logs.length], { extrapolateRight: "clamp" }));

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ opacity, transform: `scale(${scale})`, fontSize: 60, fontWeight: "bold", textShadow: "0 0 10px #00ffcc" }}>
        NICO-ANALYZER v4.0.1
      </div>
      
      <div style={{ position: "absolute", top: 50, left: 50, fontSize: 24, textAlign: "left" }}>
        {logs.slice(0, visibleLogs).map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
