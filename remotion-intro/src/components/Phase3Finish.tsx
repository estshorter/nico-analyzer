import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Phase3Finish: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const scale = spring({
    frame,
    fps,
    config: { damping: 12 },
  });
  
  // 最後の暗転を削除（Opacityは常に1）
  const opacity = 1;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity }}>
      <div style={{ transform: `scale(${scale})`, textAlign: "center" }}>
        <div style={{ fontSize: 100, fontWeight: "bold", color: "#fff", textShadow: "0 0 30px #00ffcc" }}>
          ANALYSIS COMPLETE
        </div>
        <div style={{ fontSize: 40, color: "#00ffcc", marginTop: 20 }}>
          READY FOR SECTOR: ONBOARD
        </div>
      </div>
    </AbsoluteFill>
  );
};
