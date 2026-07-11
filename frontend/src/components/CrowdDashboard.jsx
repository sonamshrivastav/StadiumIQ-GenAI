import { useState, useEffect } from 'react';
import { getCrowdData } from '../utils/api';

export default function CrowdDashboard({ stadiumId }) {
  const [crowdData, setCrowdData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCrowd = async () => {
    if (!stadiumId) return;
    setIsLoading(true);
    try {
      const data = await getCrowdData(stadiumId);
      setCrowdData(data);
    } catch (error) {
      // Use mock data if backend is not running
      setCrowdData(generateMockData(stadiumId));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCrowd();
    const interval = setInterval(fetchCrowd, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, [stadiumId]);

  if (!crowdData) {
    return (
      <div className="crowd-dashboard" style={{ padding: '16px', color: '#556380', textAlign: 'center' }}>
        Loading crowd data...
      </div>
    );
  }

  return (
    <div className="crowd-dashboard">
      {/* Overview Stats */}
      <div className="crowd-overview">
        <div className="crowd-stat">
          <div className="crowd-stat__value">{crowdData.occupancy_pct}%</div>
          <div className="crowd-stat__label">Occupancy</div>
        </div>
        <div className="crowd-stat">
          <div className="crowd-stat__value" style={{ color: '#f5a623' }}>
            {crowdData.total_inside?.toLocaleString()}
          </div>
          <div className="crowd-stat__label">Inside Now</div>
        </div>
      </div>

      {/* Alerts */}
      {crowdData.alerts && crowdData.alerts.length > 0 && (
        <div>
          {crowdData.alerts.slice(0, 3).map((alert, i) => (
            <div key={i} className={`crowd-alert ${alert.level}`}>
              {alert.message}
            </div>
          ))}
        </div>
      )}

      {/* Zone Bars */}
      {crowdData.zones && crowdData.zones.map((zone, i) => (
        <div key={i} className="crowd-zone-bar">
          <div className="crowd-zone-bar__header">
            <span className="crowd-zone-bar__name">{zone.zone}</span>
            <span className={`crowd-zone-bar__value ${zone.status}`}>
              {zone.density_pct}%
            </span>
          </div>
          <div className="crowd-zone-bar__track">
            <div
              className={`crowd-zone-bar__fill ${zone.status}`}
              style={{ width: `${zone.density_pct}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function generateMockData(stadiumId) {
  const zones = ['North Gate', 'South Gate', 'East Gate', 'West Gate', 'Main Concourse', 'Upper Deck', 'Lower Bowl', 'VIP Section'];
  const zoneData = zones.map(zone => {
    const density = Math.floor(Math.random() * 75) + 20;
    return {
      zone,
      density_pct: density,
      people_count: Math.floor(density * 100),
      status: density > 85 ? 'critical' : density > 65 ? 'high' : density > 40 ? 'moderate' : 'low',
      wait_time_min: Math.max(0, Math.floor((density - 30) * 0.3)),
    };
  });

  const totalInside = zoneData.reduce((sum, z) => sum + z.people_count, 0);

  return {
    stadium_id: stadiumId,
    stadium_name: 'Stadium',
    total_capacity: 82500,
    total_inside: totalInside,
    occupancy_pct: Math.round((totalInside / 82500) * 100 * 10) / 10,
    zones: zoneData,
    alerts: zoneData
      .filter(z => z.density_pct > 75)
      .map(z => ({
        level: z.density_pct > 85 ? 'critical' : 'warning',
        zone: z.zone,
        message: z.density_pct > 85
          ? `⚠️ ${z.zone} at ${z.density_pct}% — consider diverting`
          : `🟡 ${z.zone} approaching capacity (${z.density_pct}%)`,
      })),
    timestamp: new Date().toISOString(),
  };
}
