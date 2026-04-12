import { Composition } from "remotion";
import { Intro } from "./Intro";
import { SlopeGraph } from "./SlopeGraph";
import { ThumbnailGraph } from "./ThumbnailGraph";
import "./index.css";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Intro"
        component={Intro}
        durationInFrames={440} // ~14.6s
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="SlopeGraph"
        component={SlopeGraph}
        durationInFrames={150 * 7} // 150 frames per genre, 7 genres
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ThumbnailGraph"
        component={ThumbnailGraph}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
