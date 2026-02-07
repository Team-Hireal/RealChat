import React, { useState, useEffect } from 'react';
import soundService from '../services/soundService';
import './Settings.css';

const Settings = ({ isOpen, onClose }) => {
  const [config, setConfig] = useState({
    apiKey: '',
    baseURL: 'https://api.anthropic.com',
    model: 'claude-3-5-sonnet-20241022',
    maxTokens: 1024,
    activeProvider: 'anthropic',
    openclawEndpoint: 'http://localhost:3000'
  });

  const [soundEnabled, setSoundEnabled] = useState(true);

  const [providerStatus, setProviderStatus] = useState({
    active: 'anthropic',
    providers: {
      anthropic: { enabled: false, active: false },
      zypher: { enabled: false, active: false },
      openclaw: { enabled: false, active: false }
    }
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadConfig();
      loadProviderStatus();
      // Load sound preference from localStorage
      const savedSoundPref = localStorage.getItem('soundEnabled');
      if (savedSoundPref !== null) {
        const enabled = savedSoundPref === 'true';
        setSoundEnabled(enabled);
        soundService.setEnabled(enabled);
      }
    }
  }, [isOpen]);

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/ai/config');
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadProviderStatus = async () => {
    try {
      const response = await fetch('/api/ai/provider');
      const data = await response.json();
      setProviderStatus(data);
    } catch (error) {
      console.error('Failed to load provider status:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      // Update configuration
      const response = await fetch('/api/ai/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: 'Configuration saved successfully!' });
        setTimeout(() => {
          setMessage({ type: '', text: '' });
        }, 3000);
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to save configuration' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save configuration: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = async (provider) => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/provider', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });

      const data = await response.json();

      if (data.success) {
        setConfig({ ...config, activeProvider: provider });
        await loadProviderStatus();
        setMessage({ type: 'success', text: `Switched to ${provider}` });
        setTimeout(() => {
          setMessage({ type: '', text: '' });
        }, 3000);
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to switch provider' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to switch provider: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setConfig({ ...config, [field]: value });
  };

  const handleSoundToggle = () => {
    const newValue = !soundEnabled;
    setSoundEnabled(newValue);
    soundService.setEnabled(newValue);
    localStorage.setItem('soundEnabled', newValue.toString());

    // Play a test sound when enabling
    if (newValue) {
      soundService.playSuccess();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>⚙️ AI Agent Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          {message.text && (
            <div className={`settings-message ${message.type}`}>
              {message.text}
            </div>
          )}

          {/* AI Provider Selection */}
          <section className="settings-section">
            <h3>🤖 AI Provider</h3>
            <p className="section-description">
              Choose which AI provider to use for processing messages
            </p>

            <div className="provider-grid">
              <div
                className={`provider-card ${config.activeProvider === 'anthropic' ? 'active' : ''} ${!providerStatus.providers.anthropic?.enabled ? 'disabled' : ''}`}
                onClick={() => providerStatus.providers.anthropic?.enabled && handleProviderChange('anthropic')}
              >
                <div className="provider-icon">🔵</div>
                <h4>Anthropic API</h4>
                <p>Direct Claude integration</p>
                <div className="provider-status">
                  {providerStatus.providers.anthropic?.enabled ? (
                    <span className="status-badge enabled">✓ Enabled</span>
                  ) : (
                    <span className="status-badge disabled">✗ Disabled</span>
                  )}
                </div>
              </div>

              <div
                className={`provider-card ${config.activeProvider === 'zypher' ? 'active' : ''} ${!providerStatus.providers.zypher?.enabled ? 'disabled' : ''}`}
                onClick={() => providerStatus.providers.zypher?.enabled && handleProviderChange('zypher')}
              >
                <div className="provider-icon">🟢</div>
                <h4>Zypher Agents</h4>
                <p>Advanced agent framework</p>
                <div className="provider-status">
                  {providerStatus.providers.zypher?.enabled ? (
                    <span className="status-badge enabled">✓ Enabled</span>
                  ) : (
                    <span className="status-badge disabled">✗ Disabled</span>
                  )}
                </div>
              </div>

              <div
                className={`provider-card ${config.activeProvider === 'openclaw' ? 'active' : ''} ${!providerStatus.providers.openclaw?.enabled ? 'disabled' : ''}`}
                onClick={() => providerStatus.providers.openclaw?.enabled && handleProviderChange('openclaw')}
              >
                <div className="provider-icon">🟣</div>
                <h4>OpenClaw Local</h4>
                <p>Local Clawdbot instance</p>
                <div className="provider-status">
                  {providerStatus.providers.openclaw?.enabled ? (
                    <span className="status-badge enabled">✓ Enabled</span>
                  ) : (
                    <span className="status-badge disabled">✗ Disabled</span>
                  )}
                </div>
              </div>
            </div>
          </section>

          {/* API Configuration */}
          <section className="settings-section">
            <h3>🔑 API Configuration</h3>
            <p className="section-description">
              Unified API key and base URL for all providers
            </p>

            <div className="form-group">
              <label htmlFor="apiKey">
                API Key
                <span className="required">*</span>
              </label>
              <div className="input-with-toggle">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  id="apiKey"
                  value={config.apiKey}
                  onChange={(e) => handleInputChange('apiKey', e.target.value)}
                  placeholder="sk-ant-xxxxx or your API key"
                />
                <button
                  type="button"
                  className="toggle-visibility"
                  onClick={() => setShowApiKey(!showApiKey)}
                >
                  {showApiKey ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              <small>Get your API key from <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer">Anthropic Console</a></small>
            </div>

            <div className="form-group">
              <label htmlFor="baseURL">Base URL</label>
              <input
                type="text"
                id="baseURL"
                value={config.baseURL}
                onChange={(e) => handleInputChange('baseURL', e.target.value)}
                placeholder="https://api.anthropic.com"
              />
              <small>API endpoint URL (usually default is fine)</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="model">Model</label>
                <select
                  id="model"
                  value={config.model}
                  onChange={(e) => handleInputChange('model', e.target.value)}
                >
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="maxTokens">Max Tokens</label>
                <input
                  type="number"
                  id="maxTokens"
                  value={config.maxTokens}
                  onChange={(e) => handleInputChange('maxTokens', parseInt(e.target.value))}
                  min="256"
                  max="4096"
                  step="256"
                />
                <small>Response length limit</small>
              </div>
            </div>
          </section>

          {/* OpenClaw Configuration */}
          <section className="settings-section">
            <h3>🟣 OpenClaw Configuration</h3>
            <p className="section-description">
              Configure connection to your local OpenClaw instance
            </p>

            <div className="form-group">
              <label htmlFor="openclawEndpoint">OpenClaw Endpoint</label>
              <input
                type="text"
                id="openclawEndpoint"
                value={config.openclawEndpoint}
                onChange={(e) => handleInputChange('openclawEndpoint', e.target.value)}
                placeholder="http://localhost:3000"
              />
              <small>URL of your local OpenClaw/Clawdbot instance</small>
            </div>
          </section>

          {/* Sound Notifications */}
          <section className="settings-section">
            <h3>🔔 Sound Notifications</h3>
            <p className="section-description">
              Enable audio notifications for app events
            </p>

            <div className="form-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={soundEnabled}
                  onChange={handleSoundToggle}
                />
                <span className="toggle-text">
                  {soundEnabled ? '🔊 Sounds Enabled' : '🔇 Sounds Disabled'}
                </span>
              </label>
              <small>
                Play sounds when AI responds, messages arrive, or actions complete
              </small>
            </div>
          </section>

          {/* Cost Estimate */}
          <section className="settings-section cost-estimate">
            <h3>💰 Estimated Cost</h3>
            <div className="cost-info">
              <div className="cost-item">
                <span className="cost-label">Per message:</span>
                <span className="cost-value">~$0.003</span>
              </div>
              <div className="cost-item">
                <span className="cost-label">100 messages/day:</span>
                <span className="cost-value">~$10/month</span>
              </div>
              <div className="cost-item">
                <span className="cost-label">500 messages/day:</span>
                <span className="cost-value">~$50/month</span>
              </div>
            </div>
            <small>💡 Tip: Use OpenClaw for free local processing</small>
          </section>
        </div>

        <div className="settings-footer">
          <button className="button button-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="button button-primary"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
