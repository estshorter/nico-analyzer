import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Phase4Complete: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const scale = spring({
    frame,
    fps,
    config: { damping: 12 },
  });
  
  const opacity = interpolate(frame, [60, 75], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity }}>
      <div style={{ transform: `scale(${scale})`, opacity: Math.min(1, scale), textAlign: "center" }}>
        <div style={{ fontSize: 80, fontWeight: "bold", color: "#fff", textShadow: "0 0 20px #fff", marginBottom: 30 }}>
          ANALYSIS COMPLETE
        </div>
        <div style={{ fontSize: 40, color: "#00ffcc" }}>
          TOTAL RECORDS PROCESSED: {data.total.toLocaleString()}
        </div>
      </div>
    </AbsoluteFill>
  );
};
