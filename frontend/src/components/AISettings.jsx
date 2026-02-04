import { useState, useEffect } from 'react';

const AISettings = () => {
  const [settings, setSettings] = useState({
    api_key: '',
    base_url: 'https://api.anthropic.com',
    model: 'claude-sonnet-4-5-20250929'
  });

  const availableModels = [
    { value: 'claude-sonnet-4-5-20250929', label: 'Claude Sonnet 4.5 (Latest)' },
    { value: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5 (Fast)' },
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet (Legacy)' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus (Legacy)' }
  ];

  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/ai-settings');
      const data = await response.json();
      if (data.success) {
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveSettings = async () => {
    setIsSaving(true);
    setMessage({ text: '', type: '' });

    try {
      const response = await fetch('http://localhost:5001/api/ai-settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ text: '✅ Settings saved!', type: 'success' });
        setTimeout(() => setMessage({ text: '', type: '' }), 3000);
      } else {
        setMessage({ text: `❌ Error: ${data.error}`, type: 'error' });
      }
    } catch (error) {
      setMessage({ text: `❌ Failed: ${error.message}`, type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  const maskApiKey = (key) => {
    if (!key || key.length < 8) return key;
    return key.substring(0, 4) + '...' + key.substring(key.length - 4);
  };

  return (
    <div className="section">
      <h3 className="section-title">🔑 AI API Settings</h3>

      <div className="input-group">
        <label className="input-label">API Key</label>
        <input
          type="password"
          className="input"
          value={settings.api_key}
          onChange={(e) => handleChange('api_key', e.target.value)}
          placeholder="sk-ant-..."
        />
        {settings.api_key && (
          <span className="input-hint">Current: {maskApiKey(settings.api_key)}</span>
        )}
      </div>

      <div className="input-group">
        <label className="input-label">Base URL</label>
        <input
          type="text"
          className="input"
          value={settings.base_url}
          onChange={(e) => handleChange('base_url', e.target.value)}
          placeholder="https://api.anthropic.com"
        />
      </div>

      <div className="input-group">
        <label className="input-label">Model</label>
        <select
          className="input"
          value={settings.model}
          onChange={(e) => handleChange('model', e.target.value)}
        >
          {availableModels.map(model => (
            <option key={model.value} value={model.value}>
              {model.label}
            </option>
          ))}
        </select>
      </div>

      <button
        className="btn btn-primary"
        onClick={saveSettings}
        disabled={isSaving}
      >
        {isSaving ? '⏳ Saving...' : '💾 Save Settings'}
      </button>

      {message.text && (
        <div style={{
          marginTop: '10px',
          padding: '8px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: '600',
          background: message.type === 'success' ? '#d4edda' : '#f8d7da',
          color: message.type === 'success' ? '#155724' : '#721c24',
          border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
        }}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default AISettings;
