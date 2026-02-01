import React from 'react';
import { useAppContext } from '../context/AppContext';
import './ContactTracking.css';

const ContactTracking = () => {
  const { state } = useAppContext();
  const { tracking } = state;

  return (
    <div className="contact-tracking">
      <h2>Replied Contacts</h2>
      <div className="tracking-container">
        {tracking.length === 0 ? (
          <div className="empty-state">No contacts replied to yet.</div>
        ) : (
          <ul className="tracking-list">
            {tracking.map((contact, index) => (
              <li key={index} className="tracking-item">
                {contact}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ContactTracking;
