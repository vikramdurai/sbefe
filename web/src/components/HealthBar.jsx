import React, { useEffect, useRef, useState } from 'react';

function HealthBar({ current, max, showNumbers = true }) {
  const [statusClass, setStatusClass] = useState('');
  const prevCurrentRef = useRef(current);
  const safeMax = Math.max(1, max || 1);
  const pct = Math.max(0, Math.min(100, (current / safeMax) * 100));

  useEffect(() => {
    if (prevCurrentRef.current > current) {
      setStatusClass('taking-damage');
    } else if (prevCurrentRef.current < current) {
      setStatusClass('healing');
    }
    prevCurrentRef.current = current;

    if (statusClass) {
      const timer = setTimeout(() => setStatusClass(''), 450);
      return () => clearTimeout(timer);
    }

    return undefined;
  }, [current, statusClass]);

  let hpColorClass = 'hp-high';
  if (pct < 40) {
    hpColorClass = 'hp-low';
  } else if (pct <= 70) {
    hpColorClass = 'hp-mid';
  }

  return (
    <section className={`hud-card hud-health ${statusClass}`}>
      <div className="hud-title">HP</div>
      <div className="hud-bar-shell">
        <div className={`hud-bar-fill ${hpColorClass}`} style={{ width: `${pct}%` }} />
      </div>
      {showNumbers && (
        <div className="hud-meta">
          {current}/{safeMax}
        </div>
      )}
    </section>
  );
}

export default HealthBar;
