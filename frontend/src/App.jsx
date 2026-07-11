import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import DetailView from './components/DetailView';
import { getStadiums, getStadiumDetails, getMatches } from './utils/api';

// Fallback stadium data if backend is not running
const FALLBACK_STADIUMS = [
  { id: 'metlife', name: 'MetLife Stadium', city: 'New York / New Jersey', country: 'USA', capacity: 82500, lat: 40.8128, lng: -74.0742 },
  { id: 'sofi', name: 'SoFi Stadium', city: 'Los Angeles', country: 'USA', capacity: 70240, lat: 33.9535, lng: -118.3392 },
  { id: 'hardrock', name: 'Hard Rock Stadium', city: 'Miami', country: 'USA', capacity: 65326, lat: 25.9580, lng: -80.2389 },
  { id: 'att', name: 'AT&T Stadium', city: 'Dallas', country: 'USA', capacity: 80000, lat: 32.7473, lng: -97.0945 },
  { id: 'nrg', name: 'NRG Stadium', city: 'Houston', country: 'USA', capacity: 72220, lat: 29.6847, lng: -95.4107 },
  { id: 'mercedes', name: 'Mercedes-Benz Stadium', city: 'Atlanta', country: 'USA', capacity: 71000, lat: 33.7553, lng: -84.4006 },
  { id: 'gillette', name: 'Gillette Stadium', city: 'Boston', country: 'USA', capacity: 65878, lat: 42.0909, lng: -71.2643 },
  { id: 'arrowhead', name: 'Arrowhead Stadium', city: 'Kansas City', country: 'USA', capacity: 76416, lat: 39.0489, lng: -94.4839 },
  { id: 'lincoln', name: 'Lincoln Financial Field', city: 'Philadelphia', country: 'USA', capacity: 69796, lat: 39.9008, lng: -75.1675 },
  { id: 'levis', name: "Levi's Stadium", city: 'San Francisco Bay Area', country: 'USA', capacity: 68500, lat: 37.4033, lng: -121.9694 },
  { id: 'lumen', name: 'Lumen Field', city: 'Seattle', country: 'USA', capacity: 69000, lat: 47.5952, lng: -122.3316 },
  { id: 'azteca', name: 'Estadio Azteca', city: 'Mexico City', country: 'Mexico', capacity: 87523, lat: 19.3029, lng: -99.1505 },
  { id: 'akron', name: 'Estadio Akron', city: 'Guadalajara', country: 'Mexico', capacity: 49850, lat: 20.6827, lng: -103.4625 },
  { id: 'bbva', name: 'Estadio BBVA', city: 'Monterrey', country: 'Mexico', capacity: 53500, lat: 25.6652, lng: -100.2446 },
  { id: 'bmo', name: 'BMO Field', city: 'Toronto', country: 'Canada', capacity: 45736, lat: 43.6332, lng: -79.4186 },
  { id: 'bcplace', name: 'BC Place', city: 'Vancouver', country: 'Canada', capacity: 54500, lat: 49.2768, lng: -123.1118 },
];

const FALLBACK_MATCHES = [
  { id: 'm1', team1: '🇧🇷 Brazil', team2: '🇳🇬 Nigeria', stadium_id: 'metlife', date: '2026-07-10', time: '18:00', group: 'Group A', status: 'upcoming' },
  { id: 'm2', team1: '🇩🇪 Germany', team2: '🇯🇵 Japan', stadium_id: 'sofi', date: '2026-07-10', time: '15:00', group: 'Group B', status: 'upcoming' },
  { id: 'm3', team1: '🇦🇷 Argentina', team2: '🇦🇺 Australia', stadium_id: 'hardrock', date: '2026-07-11', time: '19:00', group: 'Group C', status: 'upcoming' },
  { id: 'm4', team1: '🇫🇷 France', team2: '🇰🇷 South Korea', stadium_id: 'att', date: '2026-07-11', time: '16:00', group: 'Group D', status: 'upcoming' },
  { id: 'm5', team1: '🇪🇸 Spain', team2: '🇨🇦 Canada', stadium_id: 'bmo', date: '2026-07-12', time: '14:00', group: 'Group E', status: 'upcoming' },
  { id: 'm6', team1: '🇬🇧 England', team2: '🇸🇳 Senegal', stadium_id: 'mercedes', date: '2026-07-12', time: '20:00', group: 'Group F', status: 'upcoming' },
];

export default function App() {
  const [stadiumId, setStadiumId] = useState('metlife');
  const [activeView, setActiveView] = useState('chat');
  const [stadiums, setStadiums] = useState(FALLBACK_STADIUMS);
  const [stadiumDetails, setStadiumDetails] = useState(null);
  const [matches, setMatches] = useState(FALLBACK_MATCHES);
  const [language, setLanguage] = useState('en');

  // Load stadiums from API
  useEffect(() => {
    async function loadStadiums() {
      try {
        const data = await getStadiums();
        if (data && data.length > 0) {
          setStadiums(data);
        }
      } catch {
        // Use fallback data
      }
    }
    loadStadiums();
  }, []);

  // Load stadium details when selection changes
  useEffect(() => {
    async function loadDetails() {
      try {
        const data = await getStadiumDetails(stadiumId);
        setStadiumDetails(data);
      } catch {
        // Use basic fallback
        const basic = stadiums.find(s => s.id === stadiumId);
        setStadiumDetails(basic || null);
      }
    }
    loadDetails();
  }, [stadiumId]);

  // Load matches
  useEffect(() => {
    async function loadMatches() {
      try {
        const data = await getMatches();
        if (data && data.length > 0) {
          setMatches(data);
        }
      } catch {
        // Use fallback
      }
    }
    loadMatches();
  }, []);

  const currentStadium = stadiums.find(s => s.id === stadiumId) || stadiums[0];
  const stadiumMatches = matches.filter(m => m.stadium_id === stadiumId);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        stadiumId={stadiumId}
        onStadiumChange={setStadiumId}
        stadiums={stadiums}
        language={language}
        onLanguageChange={setLanguage}
      />

      {/* Header */}
      <Header stadium={currentStadium} stadiumId={stadiumId} />

      {/* Main Content */}
      <div className="main-content">
        {/* Left: Chat Panel */}
        <ChatPanel stadiumId={stadiumId} language={language} />

        {/* Right: Dynamic Detail Dashboards */}
        <DetailView
          activeView={activeView}
          stadiumId={stadiumId}
          currentStadium={currentStadium}
          facilities={stadiumDetails?.facilities}
          matches={matches}
        />
      </div>
    </div>
  );
}
