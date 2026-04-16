import React, { useEffect, useRef, useState } from 'react';

function ExperienceBar({ currentXP, xpToNextLevel, currentRung, level }) {
  const [leveledUp, setLeveledUp] = useState(false);
  const prevLevelRef = useRef(level);
  const safeTarget = Math.max(1, xpToNextLevel || 1);
  const pct = Math.max(0, Math.min(100, (currentXP / safeTarget) * 100));

  useEffect(() => {
    if (level > prevLevelRef.current) {
      setLeveledUp(true);
      const timer = setTimeout(() => setLeveledUp(false), 1300);
      prevLevelRef.current = level;
      return () => clearTimeout(timer);
    }

    prevLevelRef.current = level;
    return undefined;
  }, [level]);

  return (
    <section className={`hud-card hud-experience ${leveledUp ? 'level-up' : ''}`}>
      <div className="hud-title">Echeladder</div>
      <div className="xp-rung">{currentRung}</div>
      <div className="hud-bar-shell">
        <div className="hud-bar-fill xp-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="hud-meta">Level {level} • {currentXP}/{safeTarget} XP</div>
      {leveledUp && <div className="xp-levelup-burst">LEVEL UP!</div>}
    </section>
  );
}

export default ExperienceBar;
