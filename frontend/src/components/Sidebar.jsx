const TRANSLATIONS = {
  en: {
    fan_services: "Fan Services",
    operations: "Operations",
    active_stadium: "Active Stadium",
    language_pref: "Language / Idioma",
    chat: "AI Assistant",
    crowd: "Crowd Monitor",
    navigate: "Navigate",
    accessibility: "Accessibility",
    transit: "Transit",
    sustainability: "Sustainability",
    ops: "Operations",
    incidents: "Incidents",
    staff: "Staff"
  },
  es: {
    fan_services: "Servicios para Fans",
    operations: "Operaciones",
    active_stadium: "Estadio Activo",
    language_pref: "Idioma / Language",
    chat: "Asistente AI",
    crowd: "Monitor de Multitudes",
    navigate: "Navegar",
    accessibility: "Accesibilidad",
    transit: "Tránsito",
    sustainability: "Sostenibilidad",
    ops: "Operaciones",
    incidents: "Incidentes",
    staff: "Personal"
  },
  fr: {
    fan_services: "Services aux Fans",
    operations: "Opérations",
    active_stadium: "Stade Actif",
    language_pref: "Langue / Language",
    chat: "Assistant IA",
    crowd: "Moniteur de Foule",
    navigate: "Naviguer",
    accessibility: "Accessibilité",
    transit: "Transport",
    sustainability: "Durabilité",
    ops: "Opérations",
    incidents: "Incidents",
    staff: "Personnel"
  },
  ar: {
    fan_services: "خدمات المشجعين",
    operations: "العمليات",
    active_stadium: "الملعب النشط",
    language_pref: "اللغة / Language",
    chat: "مساعد الذكاء الاصطناعي",
    crowd: "مراقب الحشود",
    navigate: "التنقل",
    accessibility: "إمكانية الوصول",
    transit: "النقل",
    sustainability: "الاستدامة",
    ops: "العمليات",
    incidents: "الحوادث",
    staff: "الموظفين"
  },
  hi: {
    fan_services: "प्रशंसक सेवाएँ",
    operations: "संचालन",
    active_stadium: "सक्रिय स्टेडियम",
    language_pref: "भाषा / Language",
    chat: "एआई सहायक",
    crowd: "भीड़ मॉनिटर",
    navigate: "नेविगेट",
    accessibility: "पहुंच",
    transit: "पारगमन",
    sustainability: "सततता",
    ops: "संचालन",
    incidents: "घटनाएँ",
    staff: "कर्मचारी"
  }
};

const NAV_ITEMS = [
  { id: 'chat', icon: '💬', label: 'AI Assistant' },
  { id: 'crowd', icon: '📊', label: 'Crowd Monitor' },
  { id: 'navigate', icon: '🗺️', label: 'Navigate' },
  { id: 'accessibility', icon: '♿', label: 'Accessibility' },
  { id: 'transit', icon: '🚌', label: 'Transit' },
  { id: 'sustainability', icon: '🌱', label: 'Sustainability' },
];

const OPS_ITEMS = [
  { id: 'ops', icon: '🔧', label: 'Operations' },
  { id: 'incidents', icon: '⚠️', label: 'Incidents' },
  { id: 'staff', icon: '👥', label: 'Staff' },
];

export default function Sidebar({ activeView, onViewChange, stadiumId, onStadiumChange, stadiums, language = 'en', onLanguageChange }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  return (
    <nav className="sidebar" aria-label="Sidebar Navigation">
      {/* Brand */}
      <div className="sidebar__brand">
        <div className="sidebar__brand-icon">⚽</div>
        <div>
          <div className="sidebar__brand-text">
            Stadium<span>IQ</span>
          </div>
          <div className="sidebar__brand-sub">FIFA World Cup 2026</div>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar__nav">
        <div className="sidebar__nav-label">{t.fan_services}</div>
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            type="button"
            className={`sidebar__nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onViewChange(item.id)}
            aria-current={activeView === item.id ? 'page' : undefined}
          >
            <span className="sidebar__nav-icon">{item.icon}</span>
            {t[item.id] || item.label}
          </button>
        ))}

        <div className="sidebar__nav-label" style={{ marginTop: '16px' }}>{t.operations}</div>
        {OPS_ITEMS.map(item => (
          <button
            key={item.id}
            type="button"
            className={`sidebar__nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onViewChange(item.id)}
            aria-current={activeView === item.id ? 'page' : undefined}
          >
            <span className="sidebar__nav-icon">{item.icon}</span>
            {t[item.id] || item.label}
          </button>
        ))}
      </div>

      {/* Stadium Selector */}
      <div className="sidebar__stadium-select">
        <label>{t.active_stadium}</label>
        <select
          value={stadiumId}
          onChange={(e) => onStadiumChange(e.target.value)}
        >
          {stadiums.map(s => (
            <option key={s.id} value={s.id}>
              {s.name} — {s.city}
            </option>
          ))}
        </select>
      </div>

      {/* Language Selector */}
      <div className="sidebar__stadium-select" style={{ marginTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '12px' }}>
        <label>{t.language_pref}</label>
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
        >
          <option value="en">English 🇺🇸</option>
          <option value="es">Español 🇪🇸</option>
          <option value="fr">Français 🇫🇷</option>
          <option value="ar">العربية 🇸🇦</option>
          <option value="hi">हिन्दी 🇮🇳</option>
        </select>
      </div>
    </nav>
  );
}
