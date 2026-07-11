import { useState, useEffect } from 'react';
import StadiumMap from './StadiumMap';
import CrowdDashboard from './CrowdDashboard';
import MatchCard from './MatchCard';
import {
  getFacilitySearch,
  getAccessibleRoute,
  getSensoryRooms,
  requestCompanion,
  getTransitAndParking,
  estimateTravelTime,
  calculateCarbon,
  getRecyclingStations,
  getSustainabilityScore,
  getIncidents,
  reportIncident,
  assignTask,
  getStaffStatus,
  getMatches
} from '../utils/api';

export default function DetailView({ activeView, stadiumId, currentStadium, facilities, matches }) {
  // Navigation / Facility search state
  const [facType, setFacType] = useState('restroom');
  const [facResults, setFacResults] = useState([]);
  const [facLoading, setFacLoading] = useState(false);

  // Accessibility state
  const [accessSection, setAccessSection] = useState('');
  const [accessRoute, setAccessRoute] = useState(null);
  const [accessLoading, setAccessLoading] = useState(false);
  const [sensoryRooms, setSensoryRooms] = useState([]);
  
  // Companion request state
  const [meetPoint, setMeetPoint] = useState('');
  const [assistType, setAssistType] = useState('wheelchair');
  const [companionReq, setCompanionReq] = useState(null);
  const [companionLoading, setCompanionLoading] = useState(false);

  // Transit state
  const [origin, setOrigin] = useState('');
  const [transitMode, setTransitMode] = useState('transit');
  const [travelEstimate, setTravelEstimate] = useState(null);
  const [travelLoading, setTravelLoading] = useState(false);
  const [transitParking, setTransitParking] = useState(null);

  // Sustainability state
  const [carbonMode, setCarbonMode] = useState('train');
  const [carbonDist, setCarbonDist] = useState(15);
  const [carbonResult, setCarbonResult] = useState(null);
  const [carbonLoading, setCarbonLoading] = useState(false);
  const [recyclingStations, setRecyclingStations] = useState([]);
  const [sustScore, setSustScore] = useState(null);

  // Operations / Incidents / Staff state
  const [incidents, setIncidents] = useState([]);
  const [incLocation, setIncLocation] = useState('');
  const [incDesc, setIncDesc] = useState('');
  const [incReporting, setIncReporting] = useState(false);

  const [taskDesc, setTaskDesc] = useState('');
  const [taskPriority, setTaskPriority] = useState('medium');
  const [assignedTaskResult, setAssignedTaskResult] = useState(null);
  const [taskAssigning, setTaskAssigning] = useState(false);

  const [staffStatus, setStaffStatus] = useState(null);
  const [opsLoading, setOpsLoading] = useState(false);

  // Load static data on tab change
  useEffect(() => {
    if (activeView === 'accessibility') {
      getSensoryRooms(stadiumId).then(data => setSensoryRooms(data.sensory_rooms || []));
    } else if (activeView === 'transit') {
      getTransitAndParking(stadiumId).then(data => setTransitParking(data));
    } else if (activeView === 'sustainability') {
      getRecyclingStations(stadiumId).then(data => setRecyclingStations(data.stations || []));
      getSustainabilityScore(stadiumId).then(data => setSustScore(data));
    } else if (activeView === 'incidents' || activeView === 'ops') {
      setOpsLoading(true);
      getIncidents(stadiumId).then(data => {
        setIncidents(data.incidents || []);
        setOpsLoading(false);
      });
      getStaffStatus(stadiumId).then(data => setStaffStatus(data));
    }
  }, [activeView, stadiumId]);

  // Run facility search
  const handleFacilitySearch = async (type) => {
    setFacType(type);
    setFacLoading(true);
    try {
      const data = await getFacilitySearch(stadiumId, type);
      setFacResults(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setFacLoading(false);
    }
  };

  // Run accessibility route planner
  const handleAccessRoute = async (e) => {
    e.preventDefault();
    if (!accessSection) return;
    setAccessLoading(true);
    try {
      const data = await getAccessibleRoute(stadiumId, accessSection);
      setAccessRoute(data);
    } catch (e) {
      console.error(e);
    } finally {
      setAccessLoading(false);
    }
  };

  // Submit companion request
  const handleCompanionRequest = async (e) => {
    e.preventDefault();
    if (!meetPoint) return;
    setCompanionLoading(true);
    try {
      const data = await requestCompanion(stadiumId, meetPoint, assistType);
      setCompanionReq(data);
    } catch (e) {
      console.error(e);
    } finally {
      setCompanionLoading(false);
    }
  };

  // Estimate travel time
  const handleTravelEstimate = async (e) => {
    e.preventDefault();
    if (!origin) return;
    setTravelLoading(true);
    try {
      const data = await estimateTravelTime(stadiumId, origin, transitMode);
      setTravelEstimate(data);
    } catch (e) {
      console.error(e);
    } finally {
      setTravelLoading(false);
    }
  };

  // Calculate carbon
  const handleCarbonCalc = async (e) => {
    if (e) e.preventDefault();
    setCarbonLoading(true);
    try {
      const data = await calculateCarbon(carbonMode, carbonDist);
      setCarbonResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setCarbonLoading(false);
    }
  };

  // Run carbon calculator initially on tab open
  useEffect(() => {
    if (activeView === 'sustainability') {
      handleCarbonCalc();
    }
  }, [activeView, carbonMode, carbonDist]);

  // Report incident
  const handleReportIncident = async (e) => {
    e.preventDefault();
    if (!incLocation || !incDesc) return;
    setIncReporting(true);
    try {
      const data = await reportIncident(stadiumId, incDesc, incLocation);
      setIncidents(prev => [data, ...prev]);
      setIncLocation('');
      setIncDesc('');
      alert(`Incident reported! Assigned ID: ${data.id}`);
    } catch (e) {
      console.error(e);
    } finally {
      setIncReporting(false);
    }
  };

  // Assign staff task
  const handleAssignTask = async (e) => {
    e.preventDefault();
    if (!taskDesc) return;
    setTaskAssigning(true);
    try {
      const data = await assignTask(stadiumId, taskDesc, taskPriority);
      setAssignedTaskResult(data);
      setTaskDesc('');
    } catch (e) {
      console.error(e);
    } finally {
      setTaskAssigning(false);
    }
  };

  const stadiumMatches = matches.filter(m => m.stadium_id === stadiumId);

  // Render view-specific panels
  switch (activeView) {
    case 'chat':
      return (
        <div className="right-panel">
          {/* Map */}
          <div className="right-panel__section">
            <div className="right-panel__section-title">🗺️ Stadium Map</div>
            <StadiumMap stadium={currentStadium} facilities={facilities} />
          </div>

          {/* Crowd density */}
          <div className="right-panel__section">
            <div className="right-panel__section-title">📊 Live Crowd Density</div>
            <CrowdDashboard stadiumId={stadiumId} />
          </div>

          {/* Matches */}
          <div className="right-panel__section">
            <div className="right-panel__section-title">
              ⚽ {stadiumMatches.length > 0 ? 'Matches at This Venue' : 'Upcoming Matches'}
            </div>
            {(stadiumMatches.length > 0 ? stadiumMatches : matches.slice(0, 3)).map(match => (
              <MatchCard key={match.id} match={match} />
            ))}
          </div>
        </div>
      );

    case 'crowd':
      return (
        <div className="detail-view">
          <h2 className="detail-title">📊 Crowd Intelligence Command</h2>
          <div className="detail-grid">
            <div className="detail-card">
              <h3>Live Density Monitor</h3>
              <CrowdDashboard stadiumId={stadiumId} />
            </div>
            <div className="detail-card">
              <h3>Exit Gate Optimizer</h3>
              <p className="card-subtext">Least congested exits recommended to reduce flow bottlenecks.</p>
              <div style={{ marginTop: 16 }}>
                <div className="best-gate-badge">
                  <span className="gate-label">Recommended exit:</span>
                  <span className="gate-value label-success">Gate D (West Gate) — 35% density</span>
                </div>
                <div className="worst-gate-badge" style={{ marginTop: 12 }}>
                  <span className="gate-label">Avoid gate:</span>
                  <span className="gate-value label-critical">Gate A (North Gate) — 88% density</span>
                </div>
                <div className="gate-tip">
                  💡 Tip: Exiting via Gate D will save approximately 15 minutes compared to Gate A.
                </div>
              </div>
            </div>
          </div>
        </div>
      );

    case 'navigate':
      return (
        <div className="detail-view">
          <h2 className="detail-title">🗺️ Facility Navigation</h2>
          <div className="detail-grid">
            <div className="detail-card card-full">
              <StadiumMap stadium={currentStadium} facilities={facilities} highlightedFacilities={facResults} />
            </div>
            <div className="detail-card">
              <h3>Find Nearest Facilities</h3>
              <div className="facility-button-row">
                <button className={`fac-btn ${facType === 'restroom' ? 'active' : ''}`} onClick={() => handleFacilitySearch('restroom')}>🚻 Restrooms</button>
                <button className={`fac-btn ${facType === 'food' ? 'active' : ''}`} onClick={() => handleFacilitySearch('food')}>🍔 Food Court</button>
                <button className={`fac-btn ${facType === 'medical' ? 'active' : ''}`} onClick={() => handleFacilitySearch('medical')}>🚑 First Aid</button>
                <button className={`fac-btn ${facType === 'exit' ? 'active' : ''}`} onClick={() => handleFacilitySearch('exit')}>🚪 Gate Exits</button>
              </div>
              
              <div className="facility-results-list" style={{ marginTop: 16 }}>
                {facLoading ? (
                  <p>Searching nearest facilities...</p>
                ) : facResults.length > 0 ? (
                  facResults.map((f, i) => (
                    <div key={i} className="facility-result-item">
                      <div className="result-name">📍 {f.name}</div>
                      <div className="result-meta">
                        <span>Section {f.section}</span>
                        <span>•</span>
                        <span>{f.distance_meters}m ({f.estimated_walk_min} min walk)</span>
                        <span>•</span>
                        <span className={`badge-${f.status}`}>{f.status?.toUpperCase() || ''}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="empty-text">Select a facility type above to search.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      );

    case 'accessibility':
      return (
        <div className="detail-view">
          <h2 className="detail-title">♿ Accessibility Concierge</h2>
          <div className="detail-grid">
            {/* Companion Request */}
            <div className="detail-card">
              <h3>Request Companion Volunteer</h3>
              <p className="card-subtext">Request volunteer assistance for navigation or wheelchair pushing.</p>
              
              {companionReq ? (
                <div className="request-success-card">
                  <div className="success-icon">✓</div>
                  <h4>Assistance Confirmed</h4>
                  <p><strong>ID:</strong> {companionReq.request_id}</p>
                  <p><strong>Volunteer:</strong> {companionReq.volunteer_name} (Blue vest)</p>
                  <p><strong>ETA:</strong> {companionReq.eta_minutes} minutes</p>
                  <p className="success-note">{companionReq.message}</p>
                  <button className="reset-btn" onClick={() => setCompanionReq(null)}>Request Another</button>
                </div>
              ) : (
                <form onSubmit={handleCompanionRequest} className="detail-form">
                  <div className="form-group">
                    <label>Meeting Location / Gate</label>
                    <input type="text" placeholder="e.g. Gate A, Section 112" value={meetPoint} onChange={e => setMeetPoint(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Assistance Type</label>
                    <select value={assistType} onChange={e => setAssistType(e.target.value)}>
                      <option value="wheelchair">Wheelchair Navigation Support</option>
                      <option value="visually-impaired">Visually Impaired Companion</option>
                      <option value="translation">Language Translation</option>
                      <option value="general">General Navigation Help</option>
                    </select>
                  </div>
                  <button type="submit" className="submit-btn" disabled={companionLoading}>
                    {companionLoading ? 'Submitting...' : 'Request Volunteer'}
                  </button>
                </form>
              )}
            </div>

            {/* Route planner */}
            <div className="detail-card">
              <h3>Accessible Route Planner</h3>
              <p className="card-subtext">Get ramp & elevator-friendly directions to your section.</p>
              
              <form onSubmit={handleAccessRoute} className="form-row">
                <input type="text" placeholder="Enter seat section (e.g. 110)" value={accessSection} onChange={e => setAccessSection(e.target.value)} required />
                <button type="submit" className="submit-btn inline-btn" disabled={accessLoading}>Find Route</button>
              </form>

              {accessLoading && <p style={{ marginTop: 16 }}>Calculating route...</p>}
              
              {accessRoute && (
                <div className="route-results" style={{ marginTop: 16 }}>
                  <h4>Accessible Directions to {accessRoute.destination}</h4>
                  <ul className="route-steps">
                    {accessRoute.route.map((step, i) => (
                      <li key={i} className="route-step">
                        <span className="step-num">{i+1}</span>
                        <span className="step-text">{step}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="route-features">
                    {accessRoute.accessibility_features.map((f, i) => (
                      <span key={i} className="feat-chip">♿ {f}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sensory Rooms */}
            <div className="detail-card card-full">
              <h3>Sensory & Quiet Rooms</h3>
              <p className="card-subtext">Calm spaces with sound-dampening & sensory tools for neurodivergent fans.</p>
              <div className="sensory-rooms-list" style={{ marginTop: 16 }}>
                {sensoryRooms.length > 0 ? (
                  sensoryRooms.map((r, i) => (
                    <div key={i} className="sensory-item">
                      <div className="sensory-header">
                        <span className="sensory-name">🧘 {r.name}</span>
                        <span className="sensory-avail label-success">{r.currently_available} spots available</span>
                      </div>
                      <div className="sensory-location">📍 Location: {r.location}</div>
                      <div className="sensory-features">
                        <strong>Includes:</strong> {r.features.join(', ')}
                      </div>
                    </div>
                  ))
                ) : (
                  <p>Loading sensory room info...</p>
                )}
              </div>
            </div>
          </div>
        </div>
      );

    case 'transit':
      return (
        <div className="detail-view">
          <h2 className="detail-title">🚌 Transit & Parking Planner</h2>
          <div className="detail-grid">
            {/* Travel Time */}
            <div className="detail-card">
              <h3>Travel Time Estimator</h3>
              <p className="card-subtext">Check travel times and match-day traffic details.</p>
              
              <form onSubmit={handleTravelEstimate} className="detail-form">
                <div className="form-group">
                  <label>Origin Address / Hotel / Station</label>
                  <input type="text" placeholder="e.g. Times Square, NY" value={origin} onChange={e => setOrigin(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label>Mode of Travel</label>
                  <select value={transitMode} onChange={e => setTransitMode(e.target.value)}>
                    <option value="transit">Public Transit</option>
                    <option value="shuttle">Free FIFA Shuttle</option>
                    <option value="rideshare">Uber / Rideshare</option>
                    <option value="driving">Driving (Personal Car)</option>
                    <option value="walking">Walking</option>
                  </select>
                </div>
                <button type="submit" className="submit-btn" disabled={travelLoading}>
                  {travelLoading ? 'Estimating...' : 'Get Time Estimate'}
                </button>
              </form>

              {travelEstimate && (
                <div className="estimate-result-card" style={{ marginTop: 16 }}>
                  <div className="est-time">🕒 {travelEstimate.estimated_minutes} min</div>
                  <div className="est-traffic">Traffic density: <span className={`traffic-${travelEstimate.traffic_status}`}>{travelEstimate.traffic_status?.toUpperCase() || ''}</span></div>
                  <p className="est-tip">💡 {travelEstimate.tip}</p>
                </div>
              )}
            </div>

            {/* Parking Lots */}
            <div className="detail-card">
              <h3>Pre-Booked Parking lots</h3>
              <p className="card-subtext">Park close to gates. Pre-booking strongly recommended to avoid queues.</p>
              
              <div className="parking-lots-list" style={{ marginTop: 16 }}>
                {transitParking?.parking?.lots ? (
                  transitParking.parking.lots.map((p, i) => (
                    <div key={i} className="parking-lot-item">
                      <div className="lot-name">🚗 {p.lot}</div>
                      <div className="lot-meta">
                        <span>Price: {p.price}</span>
                        <span>•</span>
                        <span>{p.distance_walk_min} min walk to gate</span>
                        <span>•</span>
                        <span className="avail-label">Capacity: {p.availability} free</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>Loading parking data...</p>
                )}
              </div>
            </div>

            {/* General Transit */}
            <div className="detail-card card-full">
              <h3>Venues Transit Overview</h3>
              <div className="transit-options-details" style={{ marginTop: 12 }}>
                {transitParking?.transit?.options ? (
                  Object.entries(transitParking.transit.options || {}).map(([mode, info], i) => (
                    <div key={i} className="transit-info-row">
                      <span className="transit-mode-label">{mode?.toUpperCase() || ''}</span>
                      <span className="transit-mode-text">{info}</span>
                    </div>
                  ))
                ) : (
                  <p>Loading transit info...</p>
                )}
              </div>
            </div>
          </div>
        </div>
      );

    case 'sustainability':
      return (
        <div className="detail-view">
          <h2 className="detail-title">🌱 Sustainability Hub</h2>
          <div className="detail-grid">
            {/* Carbon Footprint */}
            <div className="detail-card">
              <h3>Carbon Footprint Calculator</h3>
              <p className="card-subtext">See the eco impact of your travel to the match.</p>
              
              <form className="detail-form">
                <div className="form-group">
                  <label>Mode of Travel</label>
                  <select value={carbonMode} onChange={e => setCarbonMode(e.target.value)}>
                    <option value="train">Train / Subway 🚇</option>
                    <option value="bus">Public Bus 🚌</option>
                    <option value="shuttle">FIFA Shuttle 🚍</option>
                    <option value="car_carpool">Carpooling 🚗</option>
                    <option value="car_solo">Solo Driving 🚘</option>
                    <option value="bicycle">Bicycle 🚲</option>
                    <option value="walking">Walking 🚶</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Travel Distance: {carbonDist} km</label>
                  <input type="range" min="1" max="100" value={carbonDist} onChange={e => setCarbonDist(parseInt(e.target.value))} />
                </div>
              </form>

              {carbonResult && (
                <div className="carbon-estimate" style={{ marginTop: 16 }}>
                  <div className="carbon-value">💨 {carbonResult.co2_kg} kg CO₂</div>
                  <div className="carbon-rating">Eco rating: <span className="green-text">{carbonResult.eco_rating}</span></div>
                  <div className="carbon-diff">{carbonResult.comparison_to_car}</div>
                  <p className="carbon-tip">💡 {carbonResult.tip}</p>
                </div>
              )}
            </div>

            {/* Waste Recycling */}
            <div className="detail-card">
              <h3>Composting & Recycling Guide</h3>
              <p className="card-subtext">Find nearby recycling bins and compost properly.</p>
              
              <div className="recycling-stations-list" style={{ marginTop: 16 }}>
                {recyclingStations.length > 0 ? (
                  recyclingStations.map((r, i) => (
                    <div key={i} className="recycling-item">
                      <div className="rec-name">♻️ {r.name}</div>
                      <div className="rec-section">Location: Section {r.section}</div>
                      <div className="rec-accepts">Accepts: {r.accepts.join(', ')}</div>
                    </div>
                  ))
                ) : (
                  <p>Loading recycling stations...</p>
                )}
              </div>
            </div>

            {/* Green Initiatives */}
            <div className="detail-card card-full">
              <h3>Eco Score & Initiatives</h3>
              {sustScore ? (
                <div>
                  <div className="sustainability-score-badge">
                    <span className="score-value">🏆 {sustScore.sustainability_score}</span>
                    <span className="score-label">FIFA Stadium Eco Certification</span>
                  </div>
                  <h4 style={{ marginTop: 16, marginBottom: 8 }}>Stadium Initiatives:</h4>
                  <ul className="sust-initiatives-list">
                    {sustScore.initiatives?.map((init, i) => (
                      <li key={i}>🌿 {init}</li>
                    ))}
                  </ul>
                  <p className="sust-footer-note" style={{ marginTop: 16, fontStyle: 'italic', color: '#889bc0' }}>
                    {sustScore.fan_impact}
                  </p>
                </div>
              ) : (
                <p>Loading eco score...</p>
              )}
            </div>
          </div>
        </div>
      );

    case 'ops':
      return (
        <div className="detail-view">
          <h2 className="detail-title">🔧 Operations Dashboard</h2>
          <div className="detail-grid">
            {/* Staff deployment */}
            <div className="detail-card">
              <h3>Roster & Deployed Staff</h3>
              {staffStatus?.staff_deployed ? (
                <div style={{ marginTop: 12 }}>
                  {Object.entries(staffStatus.staff_deployed || {}).map(([dept, counts], i) => (
                    <div key={i} className="staff-row">
                      <div className="staff-dept-label">
                        <span>👥 {dept?.toUpperCase() || ''}</span>
                        <span>{counts.active} / {counts.total} active</span>
                      </div>
                      <div className="staff-track">
                        <div className="staff-fill" style={{ width: `${(counts.active / counts.total) * 100}%` }}></div>
                      </div>
                    </div>
                  ))}
                  <div style={{ marginTop: 16 }}>
                    <p><strong>Next shift change:</strong> {staffStatus.shift_change_in}</p>
                    <p><strong>Team morale index:</strong> {staffStatus.morale}</p>
                  </div>
                </div>
              ) : (
                <p>Loading staff status...</p>
              )}
            </div>

            {/* Assign Tasks */}
            <div className="detail-card">
              <h3>Assign Operational Task</h3>
              <p className="card-subtext">Direct ground staff or volunteers to resolve issues quickly.</p>
              
              {assignedTaskResult ? (
                <div className="task-assigned-card">
                  <div className="success-icon">✓</div>
                  <h4>Task Assigned Successfully</h4>
                  <p><strong>Task ID:</strong> {assignedTaskResult.task_id}</p>
                  <p><strong>Assigned To:</strong> {assignedTaskResult.assigned_to}</p>
                  <p><strong>Status:</strong> {assignedTaskResult.status?.toUpperCase() || ''}</p>
                  <p><strong>ETA:</strong> {assignedTaskResult.eta_minutes} minutes</p>
                  <button className="reset-btn" onClick={() => setAssignedTaskResult(null)}>Assign Another</button>
                </div>
              ) : (
                <form onSubmit={handleAssignTask} className="detail-form">
                  <div className="form-group">
                    <label>Task / Instruction Description</label>
                    <input type="text" placeholder="e.g. Inspect restroom Section 104 for water spill" value={taskDesc} onChange={e => setTaskDesc(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Priority Level</label>
                    <select value={taskPriority} onChange={e => setTaskPriority(e.target.value)}>
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High (Immediate deployment)</option>
                      <option value="critical">Critical (Safety hazard)</option>
                    </select>
                  </div>
                  <button type="submit" className="submit-btn" disabled={taskAssigning}>
                    {taskAssigning ? 'Assigning...' : 'Assign Staff Task'}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      );

    case 'incidents':
      return (
        <div className="detail-view">
          <h2 className="detail-title">⚠️ Operational Incidents Logs</h2>
          <div className="detail-grid">
            {/* Report Form */}
            <div className="detail-card">
              <h3>Log New Incident</h3>
              <p className="card-subtext">Report spills, facility breakages, or medical incidents.</p>
              <form onSubmit={handleReportIncident} className="detail-form">
                <div className="form-group">
                  <label>Incident Location</label>
                  <input type="text" placeholder="e.g. Upper Deck Section 312" value={incLocation} onChange={e => setIncLocation(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label>Incident Description</label>
                  <input type="text" placeholder="e.g. Blocked gate exit causing crowd pool" value={incDesc} onChange={e => setIncDesc(e.target.value)} required />
                </div>
                <button type="submit" className="submit-btn" disabled={incReporting}>
                  {incReporting ? 'Logging...' : 'Report Incident'}
                </button>
              </form>
            </div>

            {/* Incidents logs */}
            <div className="detail-card card-full">
              <h3>Incident Response Log</h3>
              <p className="card-subtext">Real-time incident response tracking (includes events parsed from Nexus report).</p>
              
              <div className="incident-logs-container" style={{ marginTop: 16, maxHeight: 400, overflowY: 'auto' }}>
                {opsLoading ? (
                  <p>Loading incident logs...</p>
                ) : incidents.length > 0 ? (
                  incidents.map((inc, i) => (
                    <div key={i} className={`incident-log-item status-${inc.status}`}>
                      <div className="inc-log-header">
                        <span className="inc-id">{inc.id}</span>
                        <span className={`inc-status-tag tag-${inc.status}`}>{inc.status?.toUpperCase() || ''}</span>
                      </div>
                      <div className="inc-desc"><strong>Issue:</strong> {inc.description}</div>
                      <div className="inc-meta">
                        <span>📍 Location: {inc.location}</span>
                        <span>•</span>
                        <span>ETA: {inc.eta_minutes} min</span>
                        <span>•</span>
                        <span>Assigned: {inc.assigned_to}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="empty-text">No incidents logged.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      );

    case 'staff':
      return (
        <div className="detail-view">
          <h2 className="detail-title">👥 Staff & Volunteer Management</h2>
          <div className="detail-grid">
            <div className="detail-card card-full">
              <h3>Roster & Volunteers Status</h3>
              <p className="card-subtext">Real-time command of volunteer personnel and shift details.</p>
              
              {staffStatus ? (
                <div style={{ marginTop: 16 }}>
                  <div className="sustainability-score-badge" style={{ background: 'rgba(25, 118, 210, 0.15)', borderColor: 'rgba(25, 118, 210, 0.3)' }}>
                    <span className="score-value" style={{ color: '#2196f3' }}>Morale Index: {staffStatus.morale}</span>
                    <span className="score-label">Deployment is operating optimally</span>
                  </div>
                  
                  <div className="staff-details-grid" style={{ marginTop: 20 }}>
                    <div className="staff-detail-card-item">
                      <h4>Roster Shifts</h4>
                      <p>Currently on shift: <strong>470 personnel</strong></p>
                      <p>Morale status: <strong>{staffStatus.morale}</strong></p>
                      <p>Next shift rotation: <strong>{staffStatus.shift_change_in}</strong></p>
                    </div>
                    <div className="staff-detail-card-item">
                      <h4>Active Standby</h4>
                      <p>Security Response: <strong>22 standby</strong></p>
                      <p>Medical Units: <strong>4 standby</strong></p>
                      <p>Maintenance Cleaners: <strong>10 standby</strong></p>
                    </div>
                  </div>
                </div>
              ) : (
                <p>Loading staff status...</p>
              )}
            </div>
          </div>
        </div>
      );

    default:
      return <div>View not implemented</div>;
  }
}
