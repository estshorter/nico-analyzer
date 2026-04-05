import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Easing } from "remotion";

export const Phase1DataLoading: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const gridOpacity = interpolate(frame, [0, 90], [0.1, 0.3]);

  const logs = [
    "INIT NICO-ANALYZER v4.0.1...",
    "SCANNING NICONICO REPOSITORY...",
    "SOURCE: genre:software_talk",
    "INGESTING VIDEO METADATA...",
    "COMPUTING RANKING SHIFTS..."
  ];
  const visibleLogs = Math.floor(interpolate(frame, [0, 40], [0, logs.length], { extrapolateRight: "clamp" }));

  const videoCount = Math.floor(interpolate(frame, [10, 80], [0, data.video_count], { 
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad) 
  }));

  const formatPaddedCount = (num: number) => {
    const padded = num.toString().padStart(7, '0');
    return padded.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  const countScale = spring({
    frame: frame - 10,
    fps,
    config: { damping: 12 },
  });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexWrap: "wrap", gap: 10, opacity: gridOpacity }}>
         {Array.from({ length: 400 }).map((_, i) => (
           <div key={i} style={{ width: 15, height: 15, backgroundColor: (frame + i) % 20 < 10 ? "#00ffcc" : "#003322", borderRadius: "50%" }} />
         ))}
      </div>

      <div style={{ position: "absolute", top: 50, left: 50, fontSize: 24, textAlign: "left", opacity: 0.8 }}>
        {logs.slice(0, visibleLogs).map((log, i) => (
          <div key={i} style={{ color: "#00ffcc" }}>{log}</div>
        ))}
      </div>

      <div style={{ 
        position: "absolute", 
        top: "50%", 
        left: "50%", 
        transform: `translate(-50%, -50%) scale(${countScale})`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center", // 横方向の中央揃え
        justifyContent: "center"
      }}>
        <div style={{ fontSize: 30, color: "#fff", marginBottom: 10, letterSpacing: 4, whiteSpace: "nowrap" }}>
          [ TOTAL ANALYZED VIDEOS ]
        </div>
        <div style={{ 
          fontSize: 130, 
          fontWeight: "bold", 
          color: "#00ffcc", 
          textShadow: "0 0 20px #00ffcc",
          fontVariantNumeric: "tabular-nums", 
          textAlign: "center",
          whiteSpace: "nowrap" // 折り返しを防いで幅を安定させる
        }}>
          {formatPaddedCount(videoCount)}
        </div>
      </div>
    </AbsoluteFill>
  );
};
