import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(true);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('branding');
  const [previewMode, setPreviewMode] = useState(false);
  const [sustainabilityData, setSustainabilityData] = useState(null);
  const [socialData, setSocialData] = useState({});

  // Login/Register states
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    business_name: ''
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData(token);
    }
  }, []);

  const fetchUserData = async (token) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsLoggedIn(true);
        fetchConfig(token);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchConfig = async (token) => {
    try {
      const response = await fetch(`${API_URL}/api/store/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const configData = await response.json();
        setConfig(configData);
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setIsLoggedIn(true);
        fetchConfig(data.token);
      } else {
        alert(data.detail || 'Login failed');
      }
    } catch (error) {
      alert('Error during login');
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerData)
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setIsLoggedIn(true);
        fetchConfig(data.token);
      } else {
        alert(data.detail || 'Registration failed');
      }
    } catch (error) {
      alert('Error during registration');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setUser(null);
    setConfig(null);
  };

  const updateConfig = async (updates) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/store/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(updates)
      });
      if (response.ok) {
        const data = await response.json();
        setConfig(data.config);
        return true;
      }
    } catch (error) {
      console.error('Error updating config:', error);
    }
    return false;
  };

  const handleSavePublish = async () => {
    setLoading(true);
    const success = await updateConfig(config);
    if (success) {
      alert('✅ Configurazione salvata e pubblicata con successo!');
    } else {
      alert('❌ Errore durante il salvataggio');
    }
    setLoading(false);
  };

  const calculateSustainability = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/sustainability/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          business_name: user.business_name,
          business_type: config?.business_description || 'General Business',
          description: config?.mission_statement || ''
        })
      });
      if (response.ok) {
        const data = await response.json();
        setSustainabilityData(data);
        alert('✅ Indice di sostenibilità calcolato!');
      } else {
        alert('❌ Errore nel calcolo della sostenibilità');
      }
    } catch (error) {
      alert('Errore: ' + error.message);
    }
    setLoading(false);
  };

  const loadPreview = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    try {
      // Fetch social data
      if (config?.google_place_id) {
        const res = await fetch(
          `${API_URL}/api/social/google-reviews?place_id=${config.google_place_id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.ok) {
          const data = await res.json();
          setSocialData(prev => ({ ...prev, google: data }));
        }
      }

      if (config?.facebook_page_id) {
        const res = await fetch(
          `${API_URL}/api/social/facebook-likes?page_id=${config.facebook_page_id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.ok) {
          const data = await res.json();
          setSocialData(prev => ({ ...prev, facebook: data }));
        }
      }

      if (config?.instagram_username) {
        const res = await fetch(
          `${API_URL}/api/social/instagram-data?username=${config.instagram_username}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.ok) {
          const data = await res.json();
          setSocialData(prev => ({ ...prev, instagram: data }));
        }
      }

      setPreviewMode(true);
    } catch (error) {
      console.error('Error loading preview:', error);
    }
    setLoading(false);
  };

  // Login/Register Screen
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-indigo-600 mb-2">Look@Me</h1>
            <p className="text-gray-600">CMS Vetrina Intelligente</p>
          </div>

          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setShowLogin(true)}
              className={`flex-1 py-2 rounded-md font-medium transition ${showLogin ? 'bg-white shadow text-indigo-600' : 'text-gray-600'}`}
            >
              Login
            </button>
            <button
              onClick={() => setShowLogin(false)}
              className={`flex-1 py-2 rounded-md font-medium transition ${!showLogin ? 'bg-white shadow text-indigo-600' : 'text-gray-600'}`}
            >
              Registrati
            </button>
          </div>

          {showLogin ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="text"
                placeholder="Username"
                value={loginData.username}
                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {loading ? 'Caricamento...' : 'Accedi'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <input
                type="text"
                placeholder="Username"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <input
                type="text"
                placeholder="Nome Attività"
                value={registerData.business_name}
                onChange={(e) => setRegisterData({ ...registerData, business_name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {loading ? 'Caricamento...' : 'Registrati'}
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  // Preview Mode
  if (previewMode) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto p-8">
          <button
            onClick={() => setPreviewMode(false)}
            className="mb-6 px-6 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-700 transition"
          >
            ← Torna all'Editor
          </button>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 shadow-2xl">
            {/* Header */}
            <div className="text-center mb-8">
              {config?.logo_url && (
                <img src={config.logo_url} alt="Logo" className="h-20 mx-auto mb-4" />
              )}
              <h1 className="text-5xl font-bold mb-2">{user?.business_name}</h1>
              {config?.mission_statement && (
                <p className="text-xl text-gray-300">{config.mission_statement}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Social Likes */}
              {config?.show_social_likes && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-blue-400">SOCIAL LIKES</h3>
                  <div className="space-y-2">
                    {socialData.facebook && (
                      <p className="text-lg">📘 Facebook: {socialData.facebook.likes || 0} likes</p>
                    )}
                    {socialData.instagram && (
                      <p className="text-lg">📸 Instagram: {socialData.instagram.followers || 0} followers</p>
                    )}
                  </div>
                </div>
              )}

              {/* Customer Satisfaction */}
              {config?.show_satisfied_customers && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-green-400">SATISFIED CUSTOMERS</h3>
                  <div className="space-y-2">
                    {socialData.google && (
                      <div>
                        <p className="text-4xl font-bold">{socialData.google.rating || 0}/5</p>
                        <p className="text-sm text-gray-400">{socialData.google.total_ratings || 0} recensioni</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Sustainability Index */}
              {config?.show_sustainability_index && sustainabilityData && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-emerald-400">SUSTAINABILITY INDEX</h3>
                  <div className="text-center">
                    <div className="text-6xl font-bold text-emerald-400">
                      {sustainabilityData.sustainability_index || 0}
                    </div>
                    <p className="text-sm text-gray-400 mt-2">su 100</p>
                  </div>
                </div>
              )}

              {/* Environmental Impact */}
              {config?.show_environmental_impact && sustainabilityData && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-green-400">ENVIRONMENTAL IMPACT</h3>
                  <div className="space-y-2">
                    <p>🌍 Environmental: {sustainabilityData.environmental_score || 0}/100</p>
                    <p>👥 Social: {sustainabilityData.social_score || 0}/100</p>
                  </div>
                </div>
              )}

              {/* Amenities */}
              {config?.show_amenities && config.amenities?.length > 0 && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-purple-400">STORE AMENITIES</h3>
                  <ul className="space-y-2">
                    {config.amenities.map((amenity, idx) => (
                      <li key={idx} className="flex items-center">
                        <span className="mr-2">✓</span> {amenity}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Additional Services */}
              {config?.show_additional_services && config.additional_services?.length > 0 && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 text-yellow-400">ADDITIONAL SERVICES</h3>
                  <ul className="space-y-2">
                    {config.additional_services.map((service, idx) => (
                      <li key={idx} className="flex items-center">
                        <span className="mr-2">●</span> {service}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main CMS Dashboard
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-indigo-600">Look@Me CMS</h1>
            <p className="text-sm text-gray-600">{user?.business_name}</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-4 sticky top-6">
              <h2 className="font-bold text-lg mb-4 text-gray-800">Sezioni</h2>
              <nav className="space-y-2">
                {[
                  { id: 'branding', label: '🎨 Branding', icon: '🎨' },
                  { id: 'visibility', label: '👁️ Visibilità Dati', icon: '👁️' },
                  { id: 'social', label: '📱 Social Media', icon: '📱' },
                  { id: 'sustainability', label: '🌱 Sostenibilità', icon: '🌱' },
                  { id: 'services', label: '⚙️ Servizi', icon: '⚙️' },
                  { id: 'recognitions', label: '🏆 Riconoscimenti', icon: '🏆' }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition ${
                      activeTab === tab.id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>

              <div className="mt-6 space-y-3">
                <button
                  onClick={loadPreview}
                  disabled={loading}
                  className="w-full px-4 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
                >
                  👁️ Anteprima Display
                </button>
                <button
                  onClick={handleSavePublish}
                  disabled={loading}
                  className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  💾 Salva & Pubblica
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm p-6">
              {activeTab === 'branding' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Branding & Immagini</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">URL Logo</label>
                      <input
                        type="url"
                        value={config.logo_url || ''}
                        onChange={(e) => setConfig({ ...config, logo_url: e.target.value })}
                        placeholder="https://esempio.com/logo.png"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Descrizione Attività</label>
                      <textarea
                        value={config.business_description || ''}
                        onChange={(e) => setConfig({ ...config, business_description: e.target.value })}
                        rows="3"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Mission Statement</label>
                      <textarea
                        value={config.mission_statement || ''}
                        onChange={(e) => setConfig({ ...config, mission_statement: e.target.value })}
                        rows="3"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'visibility' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Visibilità Dati</h2>
                  <div className="space-y-4">
                    {[
                      { key: 'show_social_likes', label: 'Social Likes' },
                      { key: 'show_satisfied_customers', label: 'Satisfied Customers' },
                      { key: 'show_sustainability_index', label: 'Sustainability Index' },
                      { key: 'show_environmental_impact', label: 'Environmental & Social Impact' },
                      { key: 'show_recognitions', label: 'Recognitions & Certifications' },
                      { key: 'show_amenities', label: 'Store Amenities' },
                      { key: 'show_additional_services', label: 'Additional Services' },
                      { key: 'show_customer_satisfaction_chart', label: 'Customer Satisfaction Chart' }
                    ].map(toggle => (
                      <div key={toggle.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">{toggle.label}</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={config[toggle.key]}
                            onChange={(e) => setConfig({ ...config, [toggle.key]: e.target.checked })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'social' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Social Media IDs</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Google Place ID</label>
                      <input
                        type="text"
                        value={config.google_place_id || ''}
                        onChange={(e) => setConfig({ ...config, google_place_id: e.target.value })}
                        placeholder="ChIJN1t_tDeuEmsRUsoyG83frY4"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">TripAdvisor Location ID</label>
                      <input
                        type="text"
                        value={config.tripadvisor_location_id || ''}
                        onChange={(e) => setConfig({ ...config, tripadvisor_location_id: e.target.value })}
                        placeholder="123456"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Facebook Page ID</label>
                      <input
                        type="text"
                        value={config.facebook_page_id || ''}
                        onChange={(e) => setConfig({ ...config, facebook_page_id: e.target.value })}
                        placeholder="1234567890"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Instagram Username</label>
                      <input
                        type="text"
                        value={config.instagram_username || ''}
                        onChange={(e) => setConfig({ ...config, instagram_username: e.target.value })}
                        placeholder="@tuoibusiness"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                      <p className="text-sm text-blue-800">
                        💡 <strong>Info:</strong> Inserisci gli ID dei tuoi profili social per visualizzare i dati in tempo reale.
                        Consulta il file <code>API_KEYS_INSTRUCTIONS.md</code> per maggiori dettagli.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'sustainability' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Sostenibilità</h2>
                  <div className="space-y-4">
                    <button
                      onClick={calculateSustainability}
                      disabled={loading}
                      className="w-full px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
                    >
                      🤖 Calcola Indice di Sostenibilità con AI
                    </button>

                    {sustainabilityData && (
                      <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
                        <h3 className="text-xl font-bold mb-4 text-green-800">Risultati</h3>
                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                            <p className="text-sm text-gray-600">Indice Sostenibilità</p>
                            <p className="text-3xl font-bold text-green-600">{sustainabilityData.sustainability_index}/100</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Score Ambientale</p>
                            <p className="text-3xl font-bold text-green-600">{sustainabilityData.environmental_score}/100</p>
                          </div>
                        </div>
                        {sustainabilityData.recommendations && (
                          <div>
                            <h4 className="font-bold mb-2">Raccomandazioni:</h4>
                            <ul className="list-disc list-inside space-y-1 text-sm">
                              {sustainabilityData.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'services' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Servizi</h2>
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-bold mb-3">Amenities (Accessibilità)</h3>
                      <div className="space-y-2">
                        {['Accessibilità per disabili', 'Pet friendly', 'WiFi gratuito', 'Parcheggio', 'Area bambini'].map(amenity => (
                          <label key={amenity} className="flex items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                            <input
                              type="checkbox"
                              checked={config.amenities?.includes(amenity)}
                              onChange={(e) => {
                                const amenities = config.amenities || [];
                                if (e.target.checked) {
                                  setConfig({ ...config, amenities: [...amenities, amenity] });
                                } else {
                                  setConfig({ ...config, amenities: amenities.filter(a => a !== amenity) });
                                }
                              }}
                              className="mr-3"
                            />
                            <span>{amenity}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-bold mb-3">Servizi Aggiuntivi</h3>
                      <div className="space-y-2">
                        {['Consegna a domicilio', 'Click & Collect', 'Servizio clienti H24', 'Garanzia estesa', 'Consulenza gratuita'].map(service => (
                          <label key={service} className="flex items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                            <input
                              type="checkbox"
                              checked={config.additional_services?.includes(service)}
                              onChange={(e) => {
                                const services = config.additional_services || [];
                                if (e.target.checked) {
                                  setConfig({ ...config, additional_services: [...services, service] });
                                } else {
                                  setConfig({ ...config, additional_services: services.filter(s => s !== service) });
                                }
                              }}
                              className="mr-3"
                            />
                            <span>{service}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'recognitions' && config && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Riconoscimenti & Certificazioni</h2>
                  <div className="space-y-4">
                    <p className="text-gray-600">Aggiungi badge e certificazioni (es. ISO, biologico, eco-friendly)</p>
                    <button
                      onClick={() => {
                        const name = prompt('Nome certificazione:');
                        const icon = prompt('URL icona:');
                        if (name && icon) {
                          const recognitions = config.recognitions || [];
                          setConfig({ ...config, recognitions: [...recognitions, { name, icon_url: icon }] });
                        }
                      }}
                      className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                    >
                      + Aggiungi Certificazione
                    </button>

                    <div className="mt-4 grid grid-cols-2 gap-4">
                      {config.recognitions?.map((rec, idx) => (
                        <div key={idx} className="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
                          <div className="flex items-center">
                            <img src={rec.icon_url} alt={rec.name} className="h-10 w-10 mr-3" />
                            <span className="font-medium">{rec.name}</span>
                          </div>
                          <button
                            onClick={() => {
                              const recognitions = config.recognitions.filter((_, i) => i !== idx);
                              setConfig({ ...config, recognitions });
                            }}
                            className="text-red-600 hover:text-red-800"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
