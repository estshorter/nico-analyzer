import React from 'react';
import { AbsoluteFill, staticFile } from 'remotion';
import data from './data/ranks.json';

export const ThumbnailGraph: React.FC = () => {
  const top5 = data.characters
    .filter(char => char.ranks.overall >= 1 && char.ranks.overall <= 5)
    .sort((a, b) => a.ranks.overall - b.ranks.overall);

  return (
    <AbsoluteFill style={{ 
      backgroundColor: '#0f172a', 
      color: 'white', 
      fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif' 
    }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)' }} />
      
      <div style={{
        position: 'relative',
        zIndex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        paddingLeft: 200,
        height: '100%'
      }}>
        {top5.map((char, index) => {
          const charName = char.id === 'whitecul' ? 'WhiteCUL' : char.name;
          return (
            <div key={char.id} style={{ 
              display: 'flex', 
              alignItems: 'center', 
              marginBottom: 40,
            }}>
              <div style={{ position: 'relative' }}>
                <img src={staticFile(char.icon)} style={{ 
                  width: 160, 
                  height: 160, 
                  borderRadius: '50%', 
                  border: `8px solid ${char.color}`,
                  boxShadow: `0 0 30px ${char.color}60`,
                  backgroundColor: '#1e293b',
                  marginRight: 60
                }} />
              </div>
              <div style={{ 
                fontSize: 90, 
                fontWeight: 900, 
                textShadow: '0 8px 16px rgba(0,0,0,0.9)',
                color: '#f8fafc',
                letterSpacing: '-1px',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center'
              }}>
                <span style={{ 
                  color: '#f8fafc', 
                  marginRight: 40,
                  width: 100,
                  textAlign: 'right'
                }}>
                  {char.ranks.overall}.
                </span>
                <span>{charName || char.id}</span>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
