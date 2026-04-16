import React, { useEffect, useMemo, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function AlchemyPanel({
  isOpen,
  sessionCode,
  playerId,
  inventory,
  grist,
  onClose,
  onCreated,
}) {
  const [slot1, setSlot1] = useState(null);
  const [slot2, setSlot2] = useState(null);
  const [mode, setMode] = useState('&&');
  const [preview, setPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [recipeHistory, setRecipeHistory] = useState([]);

  useEffect(() => {
    if (!isOpen || !sessionCode || !playerId) {
      return;
    }

    fetch(`${API_URL}/api/sessions/${sessionCode}/players/${playerId}/alchemy/state`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.recipeHistory)) {
          setRecipeHistory(data.recipeHistory);
        }
      })
      .catch(() => {});
  }, [isOpen, sessionCode, playerId]);

  const canPreview = useMemo(() => !!slot1 && !!slot2 && !!mode, [slot1, slot2, mode]);

  const runPreview = async () => {
    if (!canPreview) return;
    setLoadingPreview(true);
    setError('');
    try {
      const res = await fetch(
        `${API_URL}/api/sessions/${sessionCode}/players/${playerId}/alchemy/preview`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ item1: slot1.name, item2: slot2.name, mode }),
        }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Preview failed');
      }
      const data = await res.json();
      setPreview(data);
    } catch (e) {
      setError(e.message);
      setPreview(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  useEffect(() => {
    setPreview(null);
    if (canPreview) {
      runPreview();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slot1, slot2, mode]);

  const handleCreate = async () => {
    if (!preview || creating) return;
    setCreating(true);
    setError('');
    try {
      const res = await fetch(
        `${API_URL}/api/sessions/${sessionCode}/players/${playerId}/alchemy/create`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ item1: slot1.name, item2: slot2.name, mode }),
        }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Alchemy failed');
      }
      const data = await res.json();
      onCreated?.(data);
      setRecipeHistory(data.recipeHistory || []);
      setSlot1(null);
      setSlot2(null);
      setPreview(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  const modeOptions = ['&&', '||', 'XOR'];

  if (!isOpen) return null;

  return (
    <div className="alchemy-overlay" role="dialog" aria-label="Alchemy Panel">
      <div className="alchemy-header">
        <div className="hud-title">Alchemiter</div>
        <button className="hud-minibtn" onClick={onClose}>Close</button>
      </div>

      <div className="alchemy-slots">
        <button className={`alchemy-slot ${slot1 ? 'filled' : ''}`}>
          <span className="slot-label">Slot 1</span>
          <span className="slot-value">{slot1 ? slot1.name : '[____]'}</span>
        </button>
        <span className="alchemy-operator-plus">+</span>
        <button className={`alchemy-slot ${slot2 ? 'filled' : ''}`}>
          <span className="slot-label">Slot 2</span>
          <span className="slot-value">{slot2 ? slot2.name : '[____]'}</span>
        </button>
        <span className="alchemy-arrow">-&gt;</span>
        <div className="alchemy-result">{preview ? preview.result : '?'}</div>
      </div>

      <div className="alchemy-mode-row">
        {modeOptions.map((operator) => (
          <button
            key={operator}
            className={`alchemy-mode-btn ${mode === operator ? 'active' : ''}`}
            onClick={() => setMode(operator)}
          >
            {operator}
          </button>
        ))}
      </div>

      <div className="alchemy-cost-box">
        {!preview && !loadingPreview && <span>Cost: select two items to preview.</span>}
        {loadingPreview && <span>Calculating recipe...</span>}
        {preview && (
          <>
            <div className="alchemy-result-summary">{preview.result} • ATK {preview.attack}</div>
            <div>
              Cost: Build {preview.cost.Build}, Amber {preview.cost.Amber}, Ruby {preview.cost.Ruby}
            </div>
            <div className="alchemy-description">{preview.description}</div>
          </>
        )}
      </div>

      {error && <div className="alchemy-error">{error}</div>}

      <button
        className="alchemy-create-btn"
        disabled={!preview || creating}
        onClick={handleCreate}
      >
        {creating ? 'ALCHEMIZING...' : 'ALCHEMIZE'}
      </button>

      <div className="alchemy-grist-line">
        Grist: Build {grist?.Build ?? 0}, Amber {grist?.Amber ?? 0}, Ruby {grist?.Ruby ?? 0}
      </div>

      <div className="alchemy-inventory-title">Your Inventory</div>
      <div className="alchemy-inventory-grid">
        {(inventory || []).map((item, idx) => (
          <button
            key={`${item.name}-${idx}`}
            className="alchemy-item-btn"
            title={`Select ${item.name}`}
            onClick={() => {
              if (!slot1) {
                setSlot1(item);
              } else if (!slot2) {
                setSlot2(item);
              } else {
                setSlot1(slot2);
                setSlot2(item);
              }
            }}
          >
            <span>{item.icon || '·'}</span>
            <span>{item.name}</span>
          </button>
        ))}
      </div>

      {!!recipeHistory.length && (
        <div className="alchemy-recipe-book">
          <div className="hud-title">Recipe Book</div>
          {recipeHistory.slice(-6).reverse().map((recipe, idx) => (
            <div key={`${recipe.result}-${idx}`} className="alchemy-recipe-row">
              {recipe.item1} {recipe.mode} {recipe.item2} = {recipe.result}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlchemyPanel;
