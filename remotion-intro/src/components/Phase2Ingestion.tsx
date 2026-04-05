import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const Phase2Ingestion: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  
  const genres = Object.keys(data.counts);
  
  // Scramble text effect
  const randomChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*";
  const getScrambled = (text: string, progress: number) => {
    if (progress >= 1) return text;
    return text.split('').map((c, i) => 
      i < progress * text.length ? c : randomChars[Math.floor(Math.random() * randomChars.length)]
    ).join('');
  };

  return (
    <AbsoluteFill style={{ padding: 100, display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
      <div style={{ width: "50%", display: "flex", flexWrap: "wrap", gap: 10, alignContent: "flex-start" }}>
         {Array.from({ length: 400 }).map((_, i) => {
           const blink = (frame + i) % 30 < 15;
           return <div key={i} style={{ width: 15, height: 15, backgroundColor: blink ? "#00ffcc" : "#005544", borderRadius: "50%" }} />
         })}
      </div>
      <div style={{ width: "40%", fontSize: 40, display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ color: "#fff", textShadow: "0 0 5px #fff", marginBottom: 20 }}>[ DATA INGESTION ]</div>
        {genres.map((genre, i) => {
          const startFrame = i * 5;
          const progress = interpolate(frame - startFrame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const count = Math.floor(interpolate(progress, [0, 1], [0, data.counts[genre] || 0]));
          
          return (
            <div key={genre} style={{ display: "flex", justifyContent: "space-between", opacity: progress > 0 ? 1 : 0 }}>
              <span style={{ color: "#ccc" }}>{getScrambled(genre.toUpperCase(), progress)}</span>
              <span style={{ fontWeight: "bold" }}>{count.toLocaleString()}</span>
            </div>
          )
        })}
      </div>
    </AbsoluteFill>
  );
};
