import React from 'react';

function CombatHUD({ inCombat, enemies, turnState, availableActions, onActionClick }) {
  if (!inCombat) {
    return null;
  }

  return (
    <section className="combat-hud">
      <div className="combat-header">
        <span className="hud-title">Strife Active</span>
        <span className={`combat-turn ${turnState === 'player' ? 'your-turn' : 'enemy-turn'}`}>
          {turnState === 'player' ? 'Your Turn' : 'Enemy Turn'}
        </span>
      </div>
      <div className="combat-enemies">
        {(enemies || []).map((enemy) => {
          const maxHp = Math.max(1, enemy.maxHp || 1);
          const hpPct = Math.max(0, Math.min(100, ((enemy.currentHp || 0) / maxHp) * 100));
          return (
            <div className="combat-enemy" key={enemy.id || enemy.name}>
              <div className="combat-enemy-row">
                <span>{enemy.name}</span>
                <span>{enemy.currentHp}/{maxHp}</span>
              </div>
              <div className="hud-bar-shell combat-enemy-bar">
                <div className="hud-bar-fill hp-low" style={{ width: `${hpPct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="combat-actions">
        {(availableActions || []).map((action) => (
          <button key={action} className="combat-action-btn" onClick={() => onActionClick?.(action)}>
            {action}
          </button>
        ))}
      </div>
    </section>
  );
}

export default CombatHUD;
