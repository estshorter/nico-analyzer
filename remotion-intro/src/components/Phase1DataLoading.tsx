import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Easing } from "remotion";

export const Phase1DataLoading: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // --- 1. Short & Cool Command ---
  const command = "./calc_ranking.py";
  const typingStart = 15;
  const typingEnd = 75; // 約2秒
  
  const charsShown = Math.floor(interpolate(frame, [typingStart, typingEnd], [0, command.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  // 移動アニメーション (タイピング終了直後)
  const moveStart = 80;
  const moveProgress = spring({
    frame: frame - moveStart,
    fps,
    config: { damping: 15 },
  });

  const commandScale = interpolate(moveProgress, [0, 1], [2, 1]);
  const commandX = interpolate(moveProgress, [0, 1], [width / 2, 50]);
  const commandY = interpolate(moveProgress, [0, 1], [height / 2, 40]);
  const translateX = interpolate(moveProgress, [0, 1], [-50, 0]);
  const translateY = interpolate(moveProgress, [0, 1], [-50, 0]);

  const cursorOpacity = Math.floor(frame / 10) % 2 === 0 ? 1 : 0;

  // --- 2. Data Loading Section ---
  const loadStart = 100;
  const loadFrame = Math.max(0, frame - loadStart);

  const gridOpacity = interpolate(loadFrame, [0, 60], [0.1, 0.3]);

  const logs = [
    "INIT NICO-ANALYZER v4.0.1...",
    "SCANNING NICONICO REPOSITORY...",
    "SOURCE: genre:software_talk",
    "INGESTING VIDEO METADATA...",
    "COMPUTING RANKING SHIFTS..."
  ];
  const visibleLogs = Math.floor(interpolate(loadFrame, [0, 40], [0, logs.length], { extrapolateRight: "clamp" }));

  const videoCount = Math.floor(interpolate(loadFrame, [10, 80], [0, data.video_count], { 
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad) 
  }));

  const formatPaddedCount = (num: number) => {
    const padded = num.toString().padStart(7, '0');
    return padded.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  const countScale = spring({
    frame: loadFrame - 10,
    fps,
    config: { damping: 12 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a", fontFamily: "monospace", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexWrap: "wrap", gap: 10, opacity: gridOpacity }}>
         {Array.from({ length: 400 }).map((_, i) => (
           <div key={i} style={{ width: 15, height: 15, backgroundColor: (loadFrame + i) % 20 < 10 ? "#00ffcc" : "#003322", borderRadius: "50%" }} />
         ))}
      </div>

      <div style={{ 
        position: "absolute", 
        left: commandX, 
        top: commandY, 
        transform: `translate(${translateX}%, ${translateY}%) scale(${commandScale})`,
        fontSize: 24, 
        display: "flex", 
        alignItems: "center",
        zIndex: 10,
        whiteSpace: "nowrap"
      }}>
        <span style={{ color: "#3b82f6", marginRight: 15, fontWeight: "bold" }}>$</span>
        <span style={{ color: "#00ffcc", textShadow: frame < moveStart ? "0 0 15px #00ffcc" : "none" }}>{command.substring(0, charsShown)}</span>
        {frame < loadStart && (
          <span style={{ width: 12, height: 24, backgroundColor: "#00ffcc", marginLeft: 5, opacity: cursorOpacity }} />
        )}
      </div>

      <div style={{ 
        position: "absolute", 
        top: 80, 
        left: 50, 
        fontSize: 20, 
        textAlign: "left", 
        opacity: interpolate(loadFrame, [0, 10], [0, 0.8], { extrapolateRight: "clamp" }) 
      }}>
        {logs.slice(0, visibleLogs).map((log, i) => (
          <div key={i} style={{ color: "#00ffcc", marginBottom: 4 }}>{"> "}{log}</div>
        ))}
      </div>

      {loadFrame > 5 && (
        <div style={{ 
          position: "absolute", 
          top: "55%", 
          left: "50%", 
          transform: `translate(-50%, -50%) scale(${countScale})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity: interpolate(loadFrame, [0, 10], [0, 1])
        }}>
          <div style={{ fontSize: 28, color: "#fff", marginBottom: 10, letterSpacing: 8, whiteSpace: "nowrap", opacity: 0.7 }}>
            [ TOTAL ANALYZED VIDEOS ]
          </div>
          <div style={{ 
            fontSize: 150, 
            fontWeight: "bold", 
            color: "#00ffcc", 
            textShadow: "0 0 30px #00ffcc",
            fontVariantNumeric: "tabular-nums", 
            textAlign: "center",
            whiteSpace: "nowrap"
          }}>
            {formatPaddedCount(videoCount)}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
