import React, { useState, useEffect } from 'react';
import useConfig from '../hooks/useConfig';
import apiService from '../services/api';
import './ConfigurationForm.css';

const ConfigurationForm = () => {
  const { config, saveConfig, isLoading } = useConfig();
  const [formData, setFormData] = useState(config);
  const [saveMessage, setSaveMessage] = useState('');
  const [availableChats, setAvailableChats] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState('');
  const [isSendingTest, setIsSendingTest] = useState(false);
  const [testMessage, setTestMessage] = useState('');

  useEffect(() => {
    setFormData(config);
  }, [config]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleScanChats = async () => {
    setIsScanning(true);
    setScanMessage('');
    setAvailableChats([]);

    try {
      const response = await apiService.scanChats(10);
      if (response.data.success) {
        setAvailableChats(response.data.chats);
        setScanMessage(`Found ${response.data.chats.length} chat(s)`);
      } else {
        setScanMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setScanMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handleSelectChat = (chatName) => {
    setFormData(prev => ({
      ...prev,
      chat_name: chatName
    }));
  };

  const handleSendTestMessage = async () => {
    setIsSendingTest(true);
    setTestMessage('');

    try {
      const message = `Test message - ${new Date().toLocaleTimeString()}`;
      const response = await apiService.sendTestMessage(message);
      if (response.data.success) {
        setTestMessage('✓ Test message sent! Now scan chats to verify.');
      } else {
        setTestMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setTestMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsSendingTest(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaveMessage('');

    const result = await saveConfig(formData);
    if (result.success) {
      setSaveMessage('Configuration saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
    } else {
      setSaveMessage(`Error: ${result.error}`);
    }
  };

  return (
    <div className="configuration-form">
      <h2>Configuration</h2>
      <div className="form-content">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="chat_name">Chat Name:</label>
            <div className="chat-name-group">
              <input
                type="text"
                id="chat_name"
                name="chat_name"
                value={formData.chat_name}
                onChange={handleChange}
                placeholder="Enter chat name or scan chats"
              />
              <button
                type="button"
                className="btn btn-secondary scan-btn"
                onClick={handleScanChats}
                disabled={isScanning}
              >
                {isScanning ? 'Scanning...' : 'Scan Chats'}
              </button>
              <button
                type="button"
                className="btn btn-secondary scan-btn"
                onClick={handleSendTestMessage}
                disabled={isSendingTest}
                title="Send a test message to the currently open chat"
              >
                {isSendingTest ? 'Sending...' : 'Send Test Message'}
              </button>
            </div>
            {testMessage && (
              <div className={`scan-message ${testMessage.includes('Error') ? 'error' : 'success'}`}>
                {testMessage}
              </div>
            )}
            {scanMessage && (
              <div className={`scan-message ${scanMessage.includes('Error') ? 'error' : 'success'}`}>
                {scanMessage}
              </div>
            )}
            {availableChats.length > 0 && (
              <div className="available-chats">
                <label>Available Chats (click to select):</label>
                <div className="chat-list">
                  {availableChats.map((chat, index) => (
                    <button
                      key={index}
                      type="button"
                      className={`chat-item ${formData.chat_name === chat ? 'selected' : ''}`}
                      onClick={() => handleSelectChat(chat)}
                    >
                      {chat}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="user_name">Your Name:</label>
            <input
              type="text"
              id="user_name"
              name="user_name"
              value={formData.user_name}
              onChange={handleChange}
              placeholder="Enter your name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="user_title">Your Title:</label>
            <input
              type="text"
              id="user_title"
              name="user_title"
              value={formData.user_title}
              onChange={handleChange}
              placeholder="Enter your title"
            />
          </div>

          <div className="form-group">
            <label htmlFor="intro_template">Intro Template:</label>
            <textarea
              id="intro_template"
              name="intro_template"
              value={formData.intro_template}
              onChange={handleChange}
              rows="3"
              placeholder="Use {{NAME}} and {{TITLE}} as placeholders"
            />
          </div>

          <div className="form-group">
            <label htmlFor="default_reply">Default Reply:</label>
            <textarea
              id="default_reply"
              name="default_reply"
              value={formData.default_reply}
              onChange={handleChange}
              rows="2"
              placeholder="Enter default reply message"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reply_mode">Reply Mode:</label>
            <select
              id="reply_mode"
              name="reply_mode"
              value={formData.reply_mode}
              onChange={handleChange}
            >
              <option value="c">Custom Reply</option>
              <option value="i">Intro Template</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="dry_run">Dry Run:</label>
            <select
              id="dry_run"
              name="dry_run"
              value={formData.dry_run}
              onChange={handleChange}
            >
              <option value="yes">Yes (Test Mode)</option>
              <option value="no">No (Live Mode)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Configuration'}
          </button>

          {saveMessage && (
            <div className={`save-message ${saveMessage.includes('Error') ? 'error' : 'success'}`}>
              {saveMessage}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ConfigurationForm;

