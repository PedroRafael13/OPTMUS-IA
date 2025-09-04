// src/components/AlertCard.js

import React from 'react';
import './AlertCard.css';

const AlertCard = ({ title, description, icon }) => {
  return (
    <div className="alert-card">
      <div className="alert-card-header">
        <span className="alert-icon">{icon}</span>
        <h4 className="alert-title">{title}</h4>
      </div>
      <p className="alert-description">{description}</p>
    </div>
  );
};

export default AlertCard;