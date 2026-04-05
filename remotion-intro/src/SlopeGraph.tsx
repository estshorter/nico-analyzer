import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, staticFile } from 'remotion';
import data from './data/ranks.json';

const GENRES = ["overall", "game", "explanation", "kitchen", "theater", "onboard", "travel"];
const GENRE_LABELS: Record<string, string> = {
  overall: "全体",
  game: "実況",
  explanation: "解説",
  kitchen: "キッチン",
  theater: "劇場",
  onboard: "車載",
  travel: "旅行"
};

const SEGMENT_DURATION = 150; // 5 seconds per segment

export const SlopeGraph: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  const isIntro = frame < SEGMENT_DURATION;
  const genreIndex = Math.max(0, Math.floor(frame / SEGMENT_DURATION) - 1);
  const currentTargetGenre = isIntro ? "game" : GENRES[genreIndex + 1];
  const nextTargetGenre = GENRES[Math.min(GENRES.length - 1, genreIndex + 2)];

  const transitionStart = SEGMENT_DURATION * 0.8; 
  const relativeFrame = frame % SEGMENT_DURATION;
  
  const progress = isIntro ? 0 : spring({
    frame: Math.max(0, relativeFrame - transitionStart),
    fps,
    config: { damping: 20 },
    durationInFrames: SEGMENT_DURATION - transitionStart,
  });

  const leftGenre = "overall";
  const displayGenre = isIntro ? "game" : (progress > 0.5 ? nextTargetGenre : currentTargetGenre);

  // マージンを削って縦のスペースを最大化
  const PADDING_TOP = 100; 
  const PADDING_BOTTOM = 40;
  const PLOT_HEIGHT = height - PADDING_TOP - PADDING_BOTTOM;
  const AXIS_LEFT = 500; 
  const AXIS_RIGHT = width - 500;
  const RANK_SPACING = PLOT_HEIGHT / 10;

  const getRankY = (rank: number) => {
    if (rank > 10 || rank < 1) return height + 1000;
    return PADDING_TOP + (rank - 0.5) * RANK_SPACING;
  };

  const getCharDisplayName = (char: typeof data.characters[0]) => {
    return char.id === 'whitecul' ? '雪さん' : char.name;
  };

  const isHighlighted = (charId: string, genre: string) => {
    if (isIntro) return false;
    if (genre === 'game' && ['maki', 'tsumugi', 'rikka', 'zunko', 'akari', 'kiritan'].includes(charId)) return true;
    if (genre === 'explanation' && ['zundamon', 'moka'].includes(charId)) return true;
    if (genre === 'kitchen' && ['yukari', 'zundamon'].includes(charId)) return true;
    if (genre === 'theater' && ['akane', 'yukari', 'moka'].includes(charId)) return true;
    if (genre === 'onboard' && ['rikka', 'karin', 'chifuyu', 'zundamon'].includes(charId)) return true;
    if (genre === 'travel' && ['minato', 'whitecul', 'zundamon'].includes(charId)) return true;
    return false;
  };

  const rightAxisOpacity = interpolate(frame, [SEGMENT_DURATION - 15, SEGMENT_DURATION], [0, 1], { 
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp'
  });

  // 描画順序を調整（下位から先に描画して、上位を上に重ねる。これにより重なりが自然になる）
  const sortedCharacters = [...data.characters].sort((a, b) => {
    const rankA = a.ranks[displayGenre as keyof typeof a.ranks] || 20;
    const rankB = b.ranks[displayGenre as keyof typeof b.ranks] || 20;
    return rankB - rankA; 
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#0f172a', color: 'white', fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)' }} />

      {/* Axis Labels */}
      <div style={{ position: 'absolute', left: AXIS_LEFT, top: PADDING_TOP - 100, transform: 'translateX(-50%)', textAlign: 'center' }}>
        <div style={{ fontSize: 56, fontWeight: 800, color: '#f8fafc', borderBottom: '4px solid #38bdf8', paddingBottom: 5 }}>{GENRE_LABELS[leftGenre]}</div>
      </div>
      <div style={{ 
        position: 'absolute', left: AXIS_RIGHT, top: PADDING_TOP - 100, transform: 'translateX(-50%)', textAlign: 'center',
        opacity: rightAxisOpacity
      }}>
        <div style={{ fontSize: 56, fontWeight: 800, color: '#f8fafc', borderBottom: '4px solid #fb7185', paddingBottom: 5 }}>{GENRE_LABELS[displayGenre]}</div>
      </div>

      <svg width={width} height={height} style={{ position: 'absolute', top: 0, left: 0 }}>
        <defs>
          <filter id="glow" filterUnits="userSpaceOnUse" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {data.characters.map((char) => {
          const rankLeft = char.ranks[leftGenre as keyof typeof char.ranks];
          const rankRightCurrent = char.ranks[currentTargetGenre as keyof typeof char.ranks];
          const rankRightNext = char.ranks[nextTargetGenre as keyof typeof char.ranks];

          const yLeft = getRankY(rankLeft);
          const yRight = interpolate(progress, [0, 1], [getRankY(rankRightCurrent), getRankY(rankRightNext)]);

          if (rankLeft > 10 && rankRightCurrent > 10 && rankRightNext > 10) return null;

          const highlighted = isHighlighted(char.id, displayGenre);
          const strokeWidth = highlighted ? 10 : 2;
          
          const isVisibleOnAxis = rankLeft <= 10 || rankRightCurrent <= 10 || rankRightNext <= 10;
          const baseOpacity = isVisibleOnAxis ? (highlighted ? 1 : 0.25) : 0;
          const finalOpacity = baseOpacity * rightAxisOpacity;

          if (finalOpacity === 0) return null;

          return (
            <g key={char.id} style={{ filter: highlighted ? `drop-shadow(0 0 10px ${char.color})` : 'none' }}>
              <path
                d={`M ${AXIS_LEFT} ${yLeft} L ${AXIS_RIGHT} ${yRight}`}
                stroke={char.color}
                strokeWidth={strokeWidth}
                strokeOpacity={finalOpacity}
                fill="none"
              />
            </g>
          );
        })}

        {!isIntro && displayGenre === 'game' && (
          <g opacity={rightAxisOpacity * 0.6}>
            <circle cx={(AXIS_LEFT + AXIS_RIGHT) / 2} cy={getRankY(3.5)} r={40} fill="none" stroke="#ef4444" strokeWidth="4" strokeDasharray="10 5" />
            <circle cx={(AXIS_LEFT + AXIS_RIGHT) / 2} cy={getRankY(7)} r={40} fill="none" stroke="#ef4444" strokeWidth="4" strokeDasharray="10 5" />
          </g>
        )}
      </svg>

      {/* Characters Icons & Names */}
      {sortedCharacters.map((char) => {
        const rankLeft = char.ranks[leftGenre as keyof typeof char.ranks];
        const rankRightCurrent = char.ranks[currentTargetGenre as keyof typeof char.ranks];
        const rankRightNext = char.ranks[nextTargetGenre as keyof typeof char.ranks];

        const yLeft = getRankY(rankLeft);
        const yRight = interpolate(progress, [0, 1], [getRankY(rankRightCurrent), getRankY(rankRightNext)]);
        const highlighted = isHighlighted(char.id, displayGenre);
        const charName = getCharDisplayName(char);

        return (
          <React.Fragment key={char.id}>
            {/* Left Icons */}
            {rankLeft <= 10 && (
              <>
                <img src={staticFile(char.icon)} style={{ 
                  position: 'absolute',
                  left: AXIS_LEFT,
                  top: yLeft,
                  transform: 'translate(-50%, -50%)',
                  width: 90, height: 90, borderRadius: '50%', 
                  border: `5px solid ${char.color}`,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.7)',
                  backgroundColor: '#1e293b'
                }} />
                <div style={{ 
                  position: 'absolute',
                  left: AXIS_LEFT - 85,
                  top: yLeft,
                  transform: 'translate(-100%, -50%)',
                  fontSize: 36, fontWeight: 800, textShadow: '0 4px 8px rgba(0,0,0,0.9)',
                  color: '#f8fafc'
                }}>
                  {charName}
                </div>
              </>
            )}
            {/* Right Icons */}
            {(char.ranks[currentTargetGenre as keyof typeof char.ranks] <= 10 || char.ranks[nextTargetGenre as keyof typeof char.ranks] <= 10) && (
              <div style={{ opacity: (yRight > height ? 0 : 1) * rightAxisOpacity }}>
                <img src={staticFile(char.icon)} style={{ 
                  position: 'absolute',
                  left: AXIS_RIGHT,
                  top: yRight,
                  transform: 'translate(-50%, -50%)',
                  width: 90, height: 90, borderRadius: '50%', 
                  border: `5px solid ${char.color}`,
                  boxShadow: highlighted ? `0 0 30px ${char.color}` : '0 8px 24px rgba(0,0,0,0.7)',
                  backgroundColor: '#1e293b'
                }} />
                <div style={{ 
                  position: 'absolute',
                  left: AXIS_RIGHT + 85,
                  top: yRight,
                  transform: 'translateY(-50%)',
                  fontSize: 36, 
                  fontWeight: 800, 
                  color: highlighted ? char.color : '#f8fafc',
                  textShadow: highlighted ? `0 0 15px ${char.color}` : '0 4px 8px rgba(0,0,0,0.9)'
                }}>
                  {charName}
                </div>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
