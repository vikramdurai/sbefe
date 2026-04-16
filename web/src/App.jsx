import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
  useLocation,
} from 'react-router-dom';
import CharacterCreator from './pages/CharacterCreator';
import SessionLobby from './pages/SessionLobby';
import GameRoom from './pages/GameRoom';

const DRAFT_KEY = 'sburb_character_draft';

/** Redirects to /lobby if a character draft exists, otherwise to /create-character */
function SmartRedirect() {
  const hasDraft = !!localStorage.getItem(DRAFT_KEY);
  return <Navigate to={hasDraft ? '/lobby' : '/create-character'} replace />;
}

/** Inner component so useLocation can be called inside <Router> */
function AppContent() {
  const location = useLocation();
  const isGame = location.pathname.startsWith('/game/');
  const hasDraft = !!localStorage.getItem(DRAFT_KEY);

  return (
    <>
      {/* Hide the global header inside the game room (it has its own topbar) */}
      {!isGame && (
        <header>
          <nav>
            <Link to="/lobby">Play</Link>
            <Link to="/create-character">
              {hasDraft ? 'Edit Character' : 'Create Character'}
            </Link>
          </nav>
        </header>
      )}

      <Routes>
        {/* Full-screen game room – no <main> wrapper */}
        <Route path="/game/:sessionCode" element={<GameRoom />} />

        {/* Standard pages wrapped in <main> for max-width / centering */}
        <Route path="/lobby" element={<main><SessionLobby /></main>} />
        <Route path="/create-character" element={<main><CharacterCreator /></main>} />

        {/* Smart default: go to lobby if draft exists, else to character creator */}
        <Route path="/" element={<SmartRedirect />} />
        <Route path="*" element={<SmartRedirect />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
