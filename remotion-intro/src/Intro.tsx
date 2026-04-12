import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { Phase1DataLoading } from "./components/Phase1DataLoading";
import { Phase2ShiftAnalysis } from "./components/Phase2ShiftAnalysis";
import data from "./data.json";

export const Intro: React.FC = () => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a", color: "#00ffcc", fontFamily: "monospace" }}>
      {/* 
        構成：
        1. Data Loading (0s - 8s = 240f): タイピングとカウント完了
        2. Shift Analysis (8s - 14.6s = 200f): メインのスロープグラフと異常検知。
      */}
      
      <Sequence from={0} durationInFrames={240}>
        <Phase1DataLoading data={data} />
      </Sequence>

      <Sequence from={240} durationInFrames={200}>
        <Phase2ShiftAnalysis data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
