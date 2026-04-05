import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const Phase3Correlation: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { ranks, anomaly } = data;
  
  const chars = Object.keys(ranks);
  
  // 描画対象の順位範囲
  const MAX_RANK = 20;

  return (
    <AbsoluteFill style={{ padding: 100, display: "flex", flexDirection: "column" }}>
      <div style={{ fontSize: 50, color: "#fff", fontWeight: "bold", marginBottom: 50, textAlign: "center", textShadow: "0 0 10px #00ffcc" }}>
        RANKING SHIFT: OVERALL vs ONBOARD
      </div>
      
      <div style={{ position: "relative", flex: 1, display: "flex", justifyContent: "space-between", padding: "0 10%" }}>
        {/* Left Axis */}
        <div style={{ position: "relative", height: "100%", width: 8, backgroundColor: "#00ffcc", boxShadow: "0 0 15px #00ffcc" }}>
          <span style={{ position: "absolute", top: -50, left: -60, color: "#00ffcc", fontSize: 30, fontWeight: "bold" }}>OVERALL</span>
          {/* Rank markers */}
          {[1, 5, 10, 15, 20].map(r => (
            <div key={r} style={{ position: "absolute", top: `${(r / MAX_RANK) * 100}%`, right: 20, color: "#00ffcc", fontSize: 20 }}>{r}</div>
          ))}
        </div>
        
        {/* Right Axis */}
        <div style={{ position: "relative", height: "100%", width: 8, backgroundColor: "#00ffcc", boxShadow: "0 0 15px #00ffcc" }}>
          <span style={{ position: "absolute", top: -50, right: -60, color: "#00ffcc", fontSize: 30, fontWeight: "bold" }}>ONBOARD</span>
          {[1, 5, 10, 15, 20].map(r => (
            <div key={r} style={{ position: "absolute", top: `${(r / MAX_RANK) * 100}%`, left: 20, color: "#00ffcc", fontSize: 20 }}>{r}</div>
          ))}
        </div>
        
        {/* Lines */}
        <svg style={{ position: "absolute", top: 0, left: "10%", width: "80%", height: "100%", overflow: "visible" }}>
          {chars.map((char, i) => {
            const overallRank = ranks[char].overall;
            const onboardRank = ranks[char].onboard;
            
            // どちらかが圏外（-1）または20位以下の場合は描画の工夫
            if (overallRank === -1 && onboardRank === -1) return null;
            
            const y1 = overallRank > 0 ? (overallRank / MAX_RANK) * 100 : 110; // 圏外は画面下へ
            const y2 = onboardRank > 0 ? (onboardRank / MAX_RANK) * 100 : 110;
            
            const isAnomaly = anomaly.target.includes(char);
            const color = isAnomaly ? "#ff00ff" : "#004433";
            const width = isAnomaly ? 10 : 2;
            const opacity = isAnomaly ? 1 : 0.4;
            
            const drawProgress = interpolate(frame - (i * 1.5), [0, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            
            if (drawProgress <= 0) return null;

            return (
              <g key={char}>
                <line 
                  x1="0%" y1={`${y1}%`} 
                  x2={`${drawProgress * 100}%`} y2={`${y1 + (y2 - y1) * drawProgress}%`} 
                  stroke={color} 
                  strokeWidth={width}
                  style={{ opacity, filter: isAnomaly ? "drop-shadow(0 0 8px #ff00ff)" : "none" }}
                />
                {isAnomaly && drawProgress >= 1 && (
                  <text 
                    x="102%" y={`${y2}%`} 
                    fill="#ff00ff" 
                    fontSize="24" 
                    fontWeight="bold" 
                    alignmentBaseline="middle"
                  >
                    {char}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* Anomaly Warning: Color changed to Yellow for better contrast */}
      {frame > 45 && (
        <div style={{ 
          position: "absolute", 
          bottom: 80, 
          left: "50%", 
          transform: "translateX(-50%)", 
          fontSize: 60, 
          color: "#ffff00", 
          fontWeight: "bold", 
          textShadow: "0 0 20px #ffff00, 0 0 40px #ff0000", 
          opacity: frame % 12 < 6 ? 1 : 0.3,
          border: "4px solid #ffff00",
          padding: "10px 40px",
          backgroundColor: "rgba(255, 0, 0, 0.2)"
        }}>
          {anomaly.message}
        </div>
      )}
    </AbsoluteFill>
  );
};
