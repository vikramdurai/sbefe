import React from 'react';

function EquipmentPanel({ specibus, equippedWeapon, onToggleInventory }) {
  return (
    <section className="hud-card hud-equipment">
      <div className="hud-title">Equipment</div>
      <div className="equip-meta">Specibus: {specibus || 'Unknownkind'}</div>
      <div className="equip-weapon-name">{equippedWeapon?.name || 'No weapon equipped'}</div>
      <div className="equip-attack">ATK {equippedWeapon?.attack ?? 0}</div>
      <ul className="equip-specials">
        {(equippedWeapon?.special || []).map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
      <button className="hud-minibtn" onClick={onToggleInventory}>Inventory</button>
    </section>
  );
}

export default EquipmentPanel;
