import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const FACILITY_ICONS = {
  food: '🍔',
  restroom: '🚻',
  medical: '🏥',
  exit: '🚪',
  accessibility: '♿',
  recycling: '♻️',
};

const FACILITY_COLORS = {
  food: '#f5a623',
  restroom: '#00a3e0',
  medical: '#ff3d57',
  exit: '#00c853',
  accessibility: '#8b5cf6',
  recycling: '#00c853',
};

export default function StadiumMap({ stadium, facilities }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    if (!mapRef.current || !stadium) return;

    // Clean up existing map
    if (mapInstance.current) {
      mapInstance.current.remove();
    }

    // Create map
    const map = L.map(mapRef.current, {
      zoomControl: false,
      attributionControl: false,
    }).setView([stadium.lat, stadium.lng], 16);

    // Dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
    }).addTo(map);

    // Add zoom control to bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Stadium center marker
    const stadiumIcon = L.divIcon({
      html: `<div style="
        background: linear-gradient(135deg, #00a3e0, #8b5cf6);
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px; border: 2px solid #fff;
        box-shadow: 0 0 16px rgba(0, 163, 224, 0.5);
      ">🏟️</div>`,
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });

    L.marker([stadium.lat, stadium.lng], { icon: stadiumIcon })
      .addTo(map)
      .bindPopup(`<strong>${stadium.name}</strong><br>${stadium.city}, ${stadium.country}<br>Capacity: ${stadium.capacity?.toLocaleString()}`);

    // Add facility markers
    if (facilities) {
      Object.entries(facilities).forEach(([type, items]) => {
        const baseType = type === 'food_courts' ? 'food' :
                         type === 'restrooms' ? 'restroom' :
                         type === 'exits' ? 'exit' : type;
        const icon = FACILITY_ICONS[baseType] || '📍';
        const color = FACILITY_COLORS[baseType] || '#00a3e0';

        items.forEach(facility => {
          if (facility.lat && facility.lng) {
            const facilityIcon = L.divIcon({
              html: `<div style="
                background: ${color}22;
                border: 1px solid ${color}88;
                width: 26px; height: 26px; border-radius: 8px;
                display: flex; align-items: center; justify-content: center;
                font-size: 13px;
                box-shadow: 0 0 8px ${color}33;
              ">${icon}</div>`,
              className: '',
              iconSize: [26, 26],
              iconAnchor: [13, 13],
            });

            L.marker([facility.lat, facility.lng], { icon: facilityIcon })
              .addTo(map)
              .bindPopup(`<strong>${facility.name}</strong><br>Section: ${facility.section}<br>Type: ${baseType}`);
          }
        });
      });
    }

    mapInstance.current = map;

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, [stadium, facilities]);

  if (!stadium) {
    return (
      <div className="stadium-map" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#556380' }}>
        Select a stadium to view the map
      </div>
    );
  }

  return <div ref={mapRef} className="stadium-map" />;
}
