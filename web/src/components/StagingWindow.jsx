import React from 'react';

/**
 * StagingWindow – shows other party members' live action drafts.
 *
 * @param {Array}  drafts  – [[player_id, draft_text], ...]  (already filtered to non-empty)
 * @param {object} players – { player_id: PlayerStatus }
 */
function StagingWindow({ drafts, players }) {
  return (
    <div className="staging-window">
      <div className="staging-header">[ PARTY STAGING ]</div>
      <div className="staging-list">
        {drafts.map(([playerId, draftText]) => {
          const player = players[playerId];
          const color = player?.color || '#ffffff';
          return (
            <div key={playerId} className="staging-entry">
              <span className="staging-player-name" style={{ color }}>
                {player?.name ?? playerId} &gt;
              </span>
              <span className="staging-text">{draftText}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default StagingWindow;
