import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, useVideoConfig } from 'remotion';

export const TerminalIntro: React.FC = () => {
  const frame = useCurrentFrame();
  
  const command = "python analyzer.py --mode comparison --year 2025";
  const charsShown = Math.floor(interpolate(frame, [10, 50], [0, command.length], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));

  const cursorOpacity = Math.floor(frame / 10) % 2 === 0 ? 1 : 0;
  const opacity = interpolate(frame, [55, 60], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ 
      backgroundColor: '#0f172a', 
      color: '#10b981', 
      fontFamily: 'monospace', 
      fontSize: 40,
      padding: 100,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      opacity
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span style={{ color: '#3b82f6', marginRight: 20 }}>$</span>
        <span>{command.substring(0, charsShown)}</span>
        <span style={{ 
          width: 20, 
          height: 40, 
          backgroundColor: '#10b981', 
          marginLeft: 5,
          opacity: cursorOpacity 
        }} />
      </div>
      {frame > 52 && (
        <div style={{ marginTop: 20, color: '#f8fafc', fontSize: 24 }}>
          {">"} Loading analysis data...
        </div>
      )}
      {frame > 55 && (
        <div style={{ marginTop: 10, color: '#f8fafc', fontSize: 24 }}>
          {">"} Data loaded successfully. Initializing visualization.
        </div>
      )}
    </AbsoluteFill>
  );
};
