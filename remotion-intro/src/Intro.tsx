import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { Phase1DataLoading } from "./components/Phase1DataLoading";
import { Phase2ShiftAnalysis } from "./components/Phase2ShiftAnalysis";
import data from "./data.json";

export const Intro: React.FC = () => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a", color: "#00ffcc", fontFamily: "monospace" }}>
      {/* 
        10秒凝縮・クリフハンガー構成：
        1. Data Loading (0s - 3.5s = 105f): カウント完了後のタメ
        2. Shift Analysis (3.5s - 10s = 195f): メインのスロープグラフと異常検知。警告が出た状態でブツッと終わる。
      */}
      
      <Sequence from={0} durationInFrames={105}>
        <Phase1DataLoading data={data} />
      </Sequence>

      <Sequence from={105} durationInFrames={195}>
        <Phase2ShiftAnalysis data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
