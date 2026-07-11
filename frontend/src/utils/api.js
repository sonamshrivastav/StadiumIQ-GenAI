/**
 * StadiumIQ — API Client
 * Communicates with the FastAPI backend
 */

const API_BASE = 'http://localhost:8000';

export async function sendChatMessage(message, stadiumId = 'metlife', language = 'en', sessionId = null) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      stadium_id: stadiumId,
      language,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }

  return response.json();
}

export async function getStadiums() {
  const response = await fetch(`${API_BASE}/api/stadiums`);
  return response.json();
}

export async function getStadiumDetails(stadiumId) {
  const response = await fetch(`${API_BASE}/api/stadiums/${stadiumId}`);
  return response.json();
}

export async function getFacilities(stadiumId) {
  const response = await fetch(`${API_BASE}/api/stadiums/${stadiumId}/facilities`);
  return response.json();
}

export async function getCrowdData(stadiumId) {
  const response = await fetch(`${API_BASE}/api/crowd/${stadiumId}`);
  return response.json();
}

export async function getMatches(stadiumId = null) {
  const url = stadiumId
    ? `${API_BASE}/api/matches?stadium_id=${stadiumId}`
    : `${API_BASE}/api/matches`;
  const response = await fetch(url);
  return response.json();
}

export function createWebSocket(stadiumId = 'metlife') {
  return new WebSocket(`ws://localhost:8000/ws/live`);
}

export async function getFacilitySearch(stadiumId, facilityType) {
  const response = await fetch(`${API_BASE}/api/stadiums/${stadiumId}/facilities/${facilityType}`);
  return response.json();
}

export async function getAccessibleRoute(stadiumId, section) {
  const response = await fetch(`${API_BASE}/api/accessibility/route/${stadiumId}/${section}`);
  return response.json();
}

export async function getSensoryRooms(stadiumId) {
  const response = await fetch(`${API_BASE}/api/accessibility/sensory-room/${stadiumId}`);
  return response.json();
}

export async function requestCompanion(stadiumId, location, type) {
  const response = await fetch(`${API_BASE}/api/accessibility/companion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stadium_id: stadiumId, current_location: location, assistance_type: type }),
  });
  return response.json();
}

export async function getTransitAndParking(stadiumId) {
  const response = await fetch(`${API_BASE}/api/transit/${stadiumId}`);
  return response.json();
}

export async function estimateTravelTime(stadiumId, origin, mode) {
  const response = await fetch(`${API_BASE}/api/transit/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stadium_id: stadiumId, origin, mode }),
  });
  return response.json();
}

export async function calculateCarbon(mode, distance) {
  const response = await fetch(`${API_BASE}/api/sustainability/carbon`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transport_mode: mode, distance_km: parseFloat(distance) }),
  });
  return response.json();
}

export async function getRecyclingStations(stadiumId) {
  const response = await fetch(`${API_BASE}/api/sustainability/recycling/${stadiumId}`);
  return response.json();
}

export async function getSustainabilityScore(stadiumId) {
  const response = await fetch(`${API_BASE}/api/sustainability/score/${stadiumId}`);
  return response.json();
}

export async function getIncidents(stadiumId) {
  const response = await fetch(`${API_BASE}/api/ops/incidents/${stadiumId}`);
  return response.json();
}

export async function reportIncident(stadiumId, description, location) {
  const response = await fetch(`${API_BASE}/api/ops/incidents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stadium_id: stadiumId, description, location }),
  });
  return response.json();
}

export async function assignTask(stadiumId, description, priority) {
  const response = await fetch(`${API_BASE}/api/ops/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stadium_id: stadiumId, task_description: description, priority }),
  });
  return response.json();
}

export async function getStaffStatus(stadiumId) {
  const response = await fetch(`${API_BASE}/api/ops/staff/${stadiumId}`);
  return response.json();
}

