import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const Phase2ShiftAnalysis: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { ranks, anomaly } = data;
  const chars = Object.keys(ranks);
  const MAX_RANK = 20;

  // 全ての線を一斉に描画するための進行度 (0.5秒で完了させる)
  const allDrawProgress = interpolate(frame, [10, 25], [0, 1], { 
    extrapolateLeft: "clamp", 
    extrapolateRight: "clamp" 
  });

  return (
    <AbsoluteFill style={{ padding: 100, display: "flex", flexDirection: "column" }}>
      <div style={{ fontSize: 50, color: "#fff", fontWeight: "bold", marginBottom: 70, textAlign: "center", textShadow: "0 0 10px #00ffcc" }}>
        RANKING SHIFT: OVERALL vs ONBOARD
      </div>
      
      <div style={{ position: "relative", flex: 1, display: "flex", justifyContent: "space-between", padding: "0 10%" }}>
        {/* Axes */}
        <div style={{ position: "relative", height: "100%", width: 10, backgroundColor: "#00ffcc", boxShadow: "0 0 15px #00ffcc" }}>
          <span style={{ position: "absolute", top: -70, left: -80, color: "#00ffcc", fontSize: 45, fontWeight: "bold" }}>OVERALL</span>
          {[1, 5, 10, 15, 20].map(r => (
            <div key={r} style={{ position: "absolute", top: `${(r / MAX_RANK) * 100}%`, right: 30, color: "#00ffcc", fontSize: 30, fontWeight: "bold", transform: "translateY(-50%)" }}>{r}</div>
          ))}
        </div>
        
        <div style={{ position: "relative", height: "100%", width: 10, backgroundColor: "#00ffcc", boxShadow: "0 0 15px #00ffcc" }}>
          <span style={{ position: "absolute", top: -70, right: -80, color: "#00ffcc", fontSize: 45, fontWeight: "bold" }}>ONBOARD</span>
          {[1, 5, 10, 15, 20].map(r => (
            <div key={r} style={{ position: "absolute", top: `${(r / MAX_RANK) * 100}%`, left: 30, color: "#00ffcc", fontSize: 30, fontWeight: "bold", transform: "translateY(-50%)" }}>{r}</div>
          ))}
        </div>
        
        {/* Lines (All Draw Simultaneously) */}
        <svg style={{ position: "absolute", top: 0, left: "10%", width: "80%", height: "100%", overflow: "visible" }}>
          {chars.map((char, i) => {
            const overallRank = ranks[char].overall;
            const onboardRank = ranks[char].onboard;
            if (overallRank === -1 && onboardRank === -1) return null;
            
            const y1 = overallRank > 0 ? (overallRank / MAX_RANK) * 100 : 110;
            const y2 = onboardRank > 0 ? (onboardRank / MAX_RANK) * 100 : 110;
            
            const isAnomaly = anomaly.target.includes(char);
            const color = isAnomaly ? "#ff00ff" : "#004433";
            const width = isAnomaly ? 10 : 2;
            const opacity = isAnomaly ? 1 : 0.4;
            
            if (allDrawProgress <= 0) return null;

            return (
              <g key={char}>
                <line 
                  x1="0%" y1={`${y1}%`} 
                  x2={`${allDrawProgress * 100}%`} y2={`${y1 + (y2 - y1) * allDrawProgress}%`} 
                  stroke={color} 
                  strokeWidth={width}
                  style={{ opacity, filter: isAnomaly ? "drop-shadow(0 0 8px #ff00ff)" : "none" }}
                />
                {isAnomaly && allDrawProgress >= 1 && (
                  <text 
                    x="105%" y={`${y2}%`} 
                    fill="#ff00ff" 
                    fontSize="40" 
                    fontWeight="bold" 
                    alignmentBaseline="middle"
                    style={{ textShadow: "0 0 10px #ff00ff" }}
                  >
                    {char}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* Anomaly Warning: Appears immediately after drawing */}
      {allDrawProgress >= 1 && frame > 60 && (
        <div style={{ 
          position: "absolute", bottom: 80, left: "50%", transform: "translateX(-50%)", 
          fontSize: 60, color: "#ffff00", fontWeight: "bold", textShadow: "0 0 20px #ffff00", 
          opacity: frame % 12 < 6 ? 1 : 0.3, border: "4px solid #ffff00", padding: "10px 40px", backgroundColor: "rgba(255, 0, 0, 0.2)"
        }}>
          {anomaly.message}
        </div>
      )}
    </AbsoluteFill>
  );
};
