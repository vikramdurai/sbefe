import React, { useEffect, useMemo, useRef, useState } from 'react';

const COLOR_BY_GRIST = {
  Build: '#9aa0a6',
  Amber: '#ff9f1c',
  Ruby: '#ff3b30',
  Shale: '#8a8a8a',
  Tar: '#6b5b95',
};

function GristDisplay({ gristCounts }) {
  const [expanded, setExpanded] = useState(false);
  const [flashMap, setFlashMap] = useState({});
  const prevRef = useRef(gristCounts || {});

  useEffect(() => {
    const nextFlash = {};
    Object.entries(gristCounts || {}).forEach(([type, value]) => {
      const prev = prevRef.current[type] || 0;
      if (value > prev) {
        nextFlash[type] = 'gain';
      } else if (value < prev) {
        nextFlash[type] = 'spend';
      }
    });

    if (Object.keys(nextFlash).length > 0) {
      setFlashMap(nextFlash);
      const timer = setTimeout(() => setFlashMap({}), 550);
      prevRef.current = { ...(gristCounts || {}) };
      return () => clearTimeout(timer);
    }

    prevRef.current = { ...(gristCounts || {}) };
    return undefined;
  }, [gristCounts]);

  const visibleEntries = useMemo(() => {
    const source = Object.entries(gristCounts || {});
    if (expanded) {
      return source;
    }
    return source.filter(([, value]) => value > 0);
  }, [gristCounts, expanded]);

  return (
    <section className="hud-card hud-grist">
      <div className="hud-title-row">
        <span className="hud-title">Grist Cache</span>
        <button className="hud-minibtn" onClick={() => setExpanded((v) => !v)}>
          {expanded ? 'Hide' : 'All'}
        </button>
      </div>
      <div className="grist-list">
        {visibleEntries.length === 0 && <div className="hud-muted">No grist yet</div>}
        {visibleEntries.map(([type, value]) => (
          <div
            key={type}
            className={`grist-row ${flashMap[type] ? `grist-${flashMap[type]}` : ''}`}
            style={{ '--grist-color': COLOR_BY_GRIST[type] || '#d7d7d7' }}
          >
            <span className="grist-type">{type}</span>
            <span className="grist-value">{value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default GristDisplay;
