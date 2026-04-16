import React from 'react';

function InventoryGrid({ visible, items, fetchModus, modusRules, onClose }) {
  if (!visible) {
    return null;
  }

  const isStackMode = (fetchModus || '').toLowerCase() === 'stack';

  return (
    <aside className="inventory-overlay">
      <div className="inventory-header">
        <div>
          <div className="hud-title">Inventory</div>
          <div className="hud-meta">Fetch Modus: {fetchModus || 'Unknown'}</div>
        </div>
        <button className="hud-minibtn" onClick={onClose}>Close</button>
      </div>
      <div className={`inventory-items ${isStackMode ? 'stack-view' : 'grid-view'}`}>
        {(items || []).map((item, idx) => {
          const blocked = isStackMode && idx !== 0;
          return (
            <button key={item.id || `${item.name}-${idx}`} className={`inv-item ${blocked ? 'blocked' : ''}`}>
              <span className="inv-icon">{item.icon || '·'}</span>
              <span className="inv-name">{item.name}</span>
              <span className="inv-qty">x{item.quantity || 1}</span>
            </button>
          );
        })}
      </div>
      {!!modusRules?.length && (
        <ul className="modus-rules">
          {modusRules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      )}
    </aside>
  );
}

export default InventoryGrid;
