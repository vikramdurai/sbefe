import React, { useEffect, useMemo, useState } from 'react';

const TYPE_CLASS = {
  dialogue: 'action-dialogue',
  examine: 'action-examine',
  navigate: 'action-navigate',
  combat: 'action-combat',
  alchemy: 'action-alchemy',
  custom: 'action-custom',
};

function ActionButtons({ actions, onActionSelect }) {
  const [cooldowns, setCooldowns] = useState({});

  const normalizedActions = useMemo(() => (actions || []).slice(0, 9), [actions]);

  useEffect(() => {
    const onKeyDown = (evt) => {
      if (evt.metaKey || evt.ctrlKey || evt.altKey || evt.shiftKey) {
        return;
      }

      const index = Number.parseInt(evt.key, 10);
      if (!Number.isFinite(index) || index < 1 || index > normalizedActions.length) {
        return;
      }

      const selected = normalizedActions[index - 1];
      if (!selected || cooldowns[index - 1]) {
        return;
      }
      evt.preventDefault();
      onActionSelect?.(selected);
      setCooldowns((prev) => ({ ...prev, [index - 1]: true }));
      setTimeout(() => {
        setCooldowns((prev) => ({ ...prev, [index - 1]: false }));
      }, 900);
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [normalizedActions, cooldowns, onActionSelect]);

  if (!normalizedActions.length) {
    return null;
  }

  return (
    <div className="action-buttons-wrap">
      {normalizedActions.map((action, idx) => {
        const typeClass = TYPE_CLASS[action.action_type] || 'action-generic';
        const coolingDown = cooldowns[idx];
        return (
          <button
            key={`${action.label}-${idx}`}
            className={`context-action-btn ${typeClass} ${coolingDown ? 'cooldown' : ''}`}
            title={action.tooltip || action.label}
            disabled={coolingDown}
            onClick={() => {
              onActionSelect?.(action);
              setCooldowns((prev) => ({ ...prev, [idx]: true }));
              setTimeout(() => {
                setCooldowns((prev) => ({ ...prev, [idx]: false }));
              }, 900);
            }}
          >
            <span className="action-key">{idx + 1}</span>
            <span className="action-icon">{action.icon || '[*]'}</span>
            <span className="action-label">{action.label}</span>
          </button>
        );
      })}
    </div>
  );
}

export default ActionButtons;
