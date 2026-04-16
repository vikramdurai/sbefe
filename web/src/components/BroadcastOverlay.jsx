import React from 'react';

/**
 * BroadcastOverlay – renders universe-wide broadcast events as animated banners.
 *
 * @param {Array}    broadcasts – [{ id, event_type, event_text, event_data, timestamp }, ...]
 * @param {function} onDismiss  – callback(id) to remove a banner
 */
function BroadcastOverlay({ broadcasts, onDismiss }) {
  if (!broadcasts.length) return null;

  return (
    <div className="broadcast-overlay">
      {broadcasts.map((b) => (
        <div
          key={b.id}
          className={`broadcast-banner event-${b.event_type ?? 'default'}`}
          onClick={() => onDismiss(b.id)}
          role="alert"
        >
          <span className="broadcast-label">!! UNIVERSE EVENT !!</span>
          <span className="broadcast-text">{b.event_text}</span>
          <span className="broadcast-dismiss" aria-label="Dismiss">×</span>
        </div>
      ))}
    </div>
  );
}

export default BroadcastOverlay;
