import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../utils/api';

const WELCOME_TRANSLATIONS = {
  en: {
    title: "Welcome to StadiumIQ",
    subtitle: "Your AI-powered guide for FIFA World Cup 2026. Ask me anything about navigation, crowds, accessibility, transit, or sustainability!",
    status_online: "Online",
    title_ai_assistant: "AI Assistant",
    input_placeholder: "Ask StadiumIQ anything...",
    quick_actions: [
      { icon: '🚻', text: 'Find nearest restroom', prompt: 'Where is the nearest restroom?' },
      { icon: '🍔', text: 'Find food nearby', prompt: 'Where can I get food nearby?' },
      { icon: '📊', text: 'Crowd levels', prompt: 'How crowded is the stadium right now?' },
      { icon: '🚪', text: 'Best exit route', prompt: 'What is the best exit to avoid crowds?' },
      { icon: '♿', text: 'Accessible routes', prompt: 'I need wheelchair accessible routes to Section 112' },
      { icon: '🚌', text: 'Transit options', prompt: 'How do I get to the stadium by public transit?' },
      { icon: '🌱', text: 'Eco tips', prompt: 'How can I reduce my carbon footprint at the match today?' },
      { icon: '📅', text: 'Match schedule', prompt: 'What matches are happening today?' },
    ],
    conn_error: "⚠️ Sorry, I couldn't connect to the StadiumIQ server. Please make sure the backend is running on port 8000.",
    try_again: "Try again",
    show_schedule: "Show match schedule",
    find_restroom: "Find restroom"
  },
  es: {
    title: "Bienvenido a StadiumIQ",
    subtitle: "Su guía con IA para la Copa Mundial de la FIFA 2026. Pregúnteme sobre navegación, multitudes, accesibilidad, transporte o sostenibilidad.",
    status_online: "En línea",
    title_ai_assistant: "Asistente AI",
    input_placeholder: "Preguntar a StadiumIQ...",
    quick_actions: [
      { icon: '🚻', text: 'Encontrar baño cercano', prompt: '¿Dónde está el baño más cercano?' },
      { icon: '🍔', text: 'Comida cercana', prompt: '¿Dónde puedo conseguir comida cerca?' },
      { icon: '📊', text: 'Nivel de multitud', prompt: '¿Qué tan lleno está el estadio ahora?' },
      { icon: '🚪', text: 'Mejor ruta de salida', prompt: '¿Cuál es la mejor salida para evitar la multitud?' },
      { icon: '♿', text: 'Rutas accesibles', prompt: 'Necesito una ruta accesible para silla de ruedas a la Sección 112' },
      { icon: '🚌', text: 'Opciones de transporte', prompt: '¿Cómo llego al estadio en transporte público?' },
      { icon: '🌱', text: 'Consejos ecológicos', prompt: '¿Cómo reduzco mi huella de carbono hoy?' },
      { icon: '📅', text: 'Calendario de partidos', prompt: '¿Qué partidos se juegan hoy?' },
    ],
    conn_error: "⚠️ Lo sentimos, no se pudo conectar al servidor de StadiumIQ. Asegúrese de que el backend se esté ejecutando en el puerto 8000.",
    try_again: "Intentar otra vez",
    show_schedule: "Ver calendario",
    find_restroom: "Buscar baño"
  },
  fr: {
    title: "Bienvenue sur StadiumIQ",
    subtitle: "Votre guide IA pour la Coupe du Monde de la FIFA 2026. Posez-moi des questions sur l'orientation, la foule, l'accessibilité, le transport ou la durabilité !",
    status_online: "En ligne",
    title_ai_assistant: "Assistant IA",
    input_placeholder: "Demander à StadiumIQ...",
    quick_actions: [
      { icon: '🚻', text: 'Trouver les toilettes', prompt: 'Où se trouvent les toilettes les plus proches ?' },
      { icon: '🍔', text: 'Trouver de la nourriture', prompt: 'Où puis-je manger à proximité ?' },
      { icon: '📊', text: 'Niveau de foule', prompt: 'Quel est le niveau d\'affluence du stade actuellement ?' },
      { icon: '🚪', text: 'Meilleure sortie', prompt: 'Quelle est la meilleure sortie pour éviter la foule ?' },
      { icon: '♿', text: 'Accès accessible', prompt: 'J\'ai besoin d\'un itinéraire accessible en fauteuil roulant pour la section 112' },
      { icon: '🚌', text: 'Options de transport', prompt: 'Comment se rendre au stade en transports en commun ?' },
      { icon: '🌱', text: 'Conseils écolo', prompt: 'Comment puis-je réduire mon empreinte carbone aujourd\'hui ?' },
      { icon: '📅', text: 'Calendrier des matchs', prompt: 'Quels matchs se jouent aujourd\'hui ?' },
    ],
    conn_error: "⚠️ Désolé, impossible de se connecter au serveur de StadiumIQ. Assurez-vous que le backend fonctionne sur le port 8000.",
    try_again: "Réessayer",
    show_schedule: "Afficher le calendrier",
    find_restroom: "Trouver les toilettes"
  },
  ar: {
    title: "مرحبًا بك في StadiumIQ",
    subtitle: "دليلك المدعوم بالذكاء الاصطناعي لكأس العالم لكرة القدم 2026. اسألني عن التنقل، الحشود، إمكانية الوصول، النقل، أو الاستدامة!",
    status_online: "متصل",
    title_ai_assistant: "مساعد الذكاء الاصطناعي",
    input_placeholder: "اسأل StadiumIQ...",
    quick_actions: [
      { icon: '🚻', text: 'العثور على أقرب دورة مياه', prompt: 'أين تقع أقرب دورة مياه؟' },
      { icon: '🍔', text: 'العثور على طعام قريب', prompt: 'أين يمكنني الحصول على طعام قريب؟' },
      { icon: '📊', text: 'مستويات الحشود', prompt: 'ما مدى ازدحام الملعب الآن؟' },
      { icon: '🚪', text: 'أفضل مسار للخروج', prompt: 'ما هو أفضل مخرج لتجنب الازدحام؟' },
      { icon: '♿', text: 'مسارات إمكانية الوصول', prompt: 'أحتاج إلى مسار مخصص للكراسي المتحركة إلى القسم 112' },
      { icon: '🚌', text: 'خيارات النقل', prompt: 'كيف يمكنني الوصول إلى الملعب بوسائل النقل العام؟' },
      { icon: '🌱', text: 'نصائح بيئية', prompt: 'كيف يمكنني تقليل بصمتي الكربونية في المباراة اليوم؟' },
      { icon: '📅', text: 'جدول المباريات', prompt: 'ما هي المباريات المقامة اليوم?' },
    ],
    conn_error: "⚠️ عذرًا، تعذر الاتصال بخادم StadiumIQ. يرجى التأكد من تشغيل الخادم الخلفي على المنفذ 8000.",
    try_again: "إعادة المحاولة",
    show_schedule: "عرض جدول المباريات",
    find_restroom: "بحث عن دورة مياه"
  },
  hi: {
    title: "StadiumIQ में आपका स्वागत है",
    subtitle: "फीफा विश्व कप 2026 के लिए आपका एआई-संचालित गाइड। नेविगेशन, भीड़, पहुंच, पारगमन या पर्यावरण के बारे में कुछ भी पूछें!",
    status_online: "ऑनलाइन",
    title_ai_assistant: "एआई सहायक",
    input_placeholder: "StadiumIQ से पूछें...",
    quick_actions: [
      { icon: '🚻', text: 'निकटतम शौचालय खोजें', prompt: 'निकटतम शौचालय कहाँ है?' },
      { icon: '🍔', text: 'पास में भोजन खोजें', prompt: 'मुझे पास में भोजन कहाँ मिल सकता है?' },
      { icon: '📊', text: 'भीड़ का स्तर', prompt: 'स्टेडियम में अभी कितनी भीड़ है?' },
      { icon: '🚪', text: 'सर्वश्रेष्ठ निकास मार्ग', prompt: 'भीड़ से बचने के लिए सबसे अच्छा निकास मार्ग क्या है?' },
      { icon: '♿', text: 'सुगम मार्ग', prompt: 'मुझे सेक्शन 112 के लिए व्हीलचेयर सुगम मार्ग चाहिए' },
      { icon: '🚌', text: 'पारगमन विकल्प', prompt: 'सार्वजनिक परिवहन द्वारा स्टेडियम कैसे पहुँचें?' },
      { icon: '🌱', text: 'पर्यावरण युक्तियाँ', prompt: 'मैच के दौरान मैं अपना कार्बन फुटप्रिंट कैसे कम करूँ?' },
      { icon: '📅', text: 'मैच अनुसूची', prompt: 'आज कौन से मैच हो रहे हैं?' },
    ],
    conn_error: "⚠️ क्षमा करें, मैं StadiumIQ सर्वर से कनेक्ट नहीं हो सका। कृपया सुनिश्चित करें कि बैकएंड पोर्ट 8000 पर चल रहा है।",
    try_again: "पुनः प्रयास करें",
    show_schedule: "मैच शेड्यूल दिखाएं",
    find_restroom: "शौचालय खोजें"
  }
};

const formatMessageText = (text) => {
  if (!text) return '';
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};

export default function ChatPanel({ stadiumId, language = 'en', onSendMessage }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const t = WELCOME_TRANSLATIONS[language] || WELCOME_TRANSLATIONS.en;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Clear chat history when switching stadium or language to keep session clean
  useEffect(() => {
    setMessages([]);
    setSuggestions([]);
  }, [stadiumId, language]);

  const handleSend = async (text) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    // Add user message
    const userMsg = { role: 'user', text: messageText, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    setSuggestions([]);

    try {
      const response = await sendChatMessage(messageText, stadiumId, language, sessionId);

      const aiMsg = {
        role: 'ai',
        text: response.reply,
        agent: response.agent_used,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);

      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error) {
      const errorMsg = {
        role: 'ai',
        text: t.conn_error,
        agent: 'system',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
      setSuggestions([t.try_again, t.show_schedule, t.find_restroom]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-panel__header">
        <div className="chat-panel__title">
          💬 {t.title_ai_assistant}
        </div>
        <div className="chat-panel__status">
          <span className="live-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: '#00c853', display: 'inline-block' }}></span>
          {t.status_online}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-panel__messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-message__icon">⚽</div>
            <h2 className="welcome-message__title">{t.title}</h2>
            <p className="welcome-message__subtitle">{t.subtitle}</p>
            <div className="welcome-message__quick-actions">
              {t.quick_actions.map((action, i) => (
                <button
                  key={i}
                  className="welcome-action"
                  onClick={() => handleSend(action.prompt)}
                >
                  <span className="welcome-action__icon">{action.icon}</span>
                  {action.text}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message chat-message--${msg.role}`}>
                <div className="chat-message__avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="chat-message__bubble">
                  {msg.agent && msg.role === 'ai' && (
                    <div className="chat-message__agent-tag">
                      {msg.agent.replace(/_/g, ' ')}
                    </div>
                  )}
                  <div className="chat-message__text" style={{ whiteSpace: 'pre-wrap' }} dangerouslySetInnerHTML={{ __html: formatMessageText(msg.text) }} />
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator">
                <div className="chat-message__avatar" style={{
                  background: 'linear-gradient(135deg, #f5a623, #ff8c42)',
                  width: 36, height: 36, borderRadius: 12,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>🤖</div>
                <div className="typing-indicator__dots">
                  <div className="typing-indicator__dot"></div>
                  <div className="typing-indicator__dot"></div>
                  <div className="typing-indicator__dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Suggestion Chips */}
      {suggestions.length > 0 && (
        <div className="chat-suggestions">
          {suggestions.map((s, i) => (
            <button
              key={i}
              className="chat-suggestion-chip"
              onClick={() => handleSend(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            className="chat-input"
            type="text"
            placeholder={t.input_placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            aria-label="Ask a question about the stadium"
          />
          <button
            className="chat-send-btn"
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
