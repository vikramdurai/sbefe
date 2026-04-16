import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

const DEFAULT_GAME_STATE = {
  player: {
    hp: { current: 88, max: 100 },
    xp: { currentXP: 30, xpToNextLevel: 100, currentRung: 'Lint-Licker', level: 1 },
    gristCounts: {
      Build: 450,
      Amber: 120,
      Ruby: 0,
      Shale: 40,
      Tar: 0,
    },
    equipment: {
      specibus: 'Hammerkind',
      equippedWeapon: {
        name: 'Claw Hammer',
        attack: 12,
        special: ['Reliable smack', 'Can pry open crates'],
      },
    },
    inventory: {
      fetchModus: 'Stack',
      modusRules: ['Only top item can be quickly retrieved'],
      items: [
        { id: 'it-hammer', name: 'Claw Hammer', icon: 'H', quantity: 1 },
        { id: 'it-card', name: 'Captchalogue Card', icon: 'C', quantity: 4 },
        { id: 'it-apple', name: 'Apple Juice Box', icon: 'J', quantity: 2 },
      ],
    },
    inCombat: false,
  },
  combat: {
    enemies: [],
    turnState: 'enemy',
    availableActions: ['Attack', 'Defend', 'Item', 'Abscond'],
  },
};

const GameStateContext = createContext(null);

function mergeState(base, patch) {
  if (!patch || typeof patch !== 'object') {
    return base;
  }

  const next = { ...base };
  Object.keys(patch).forEach((key) => {
    const prevValue = base[key];
    const patchValue = patch[key];
    if (
      prevValue &&
      typeof prevValue === 'object' &&
      !Array.isArray(prevValue) &&
      patchValue &&
      typeof patchValue === 'object' &&
      !Array.isArray(patchValue)
    ) {
      next[key] = mergeState(prevValue, patchValue);
    } else {
      next[key] = patchValue;
    }
  });

  return next;
}

export function GameStateProvider({ children, initialState }) {
  const [gameState, setGameState] = useState(() => mergeState(DEFAULT_GAME_STATE, initialState || {}));

  const applyGameStatePatch = useCallback((patch) => {
    setGameState((prev) => mergeState(prev, patch));
  }, []);

  const setInCombat = useCallback((inCombat) => {
    setGameState((prev) => ({
      ...prev,
      player: {
        ...prev.player,
        inCombat,
      },
    }));
  }, []);

  const value = useMemo(
    () => ({
      gameState,
      applyGameStatePatch,
      setInCombat,
    }),
    [gameState, applyGameStatePatch, setInCombat]
  );

  return <GameStateContext.Provider value={value}>{children}</GameStateContext.Provider>;
}

export function useGameState() {
  const ctx = useContext(GameStateContext);
  if (!ctx) {
    throw new Error('useGameState must be used inside a GameStateProvider');
  }
  return ctx;
}
