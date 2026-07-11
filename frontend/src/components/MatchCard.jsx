export default function MatchCard({ match, onAskAbout }) {
  return (
    <div className="match-card" onClick={() => onAskAbout && onAskAbout(match)}>
      <div className="match-card__group">{match.group}</div>
      <div className="match-card__teams">
        <span>{match.team1}</span>
        <span className="match-card__vs">vs</span>
        <span>{match.team2}</span>
      </div>
      <div className="match-card__info">
        <span>📅 {match.date} • {match.time}</span>
        <button
          className="match-card__ask-btn"
          onClick={(e) => {
            e.stopPropagation();
            onAskAbout && onAskAbout(match);
          }}
        >
          Ask AI →
        </button>
      </div>
    </div>
  );
}
