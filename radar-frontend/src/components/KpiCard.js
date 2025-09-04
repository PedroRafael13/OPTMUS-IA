// src/components/KpiCard.js
import React from 'react';
import './KpiCard.css';

const KpiCard = ({ title, value, subtitle, change, icon }) => {
  const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';

  return (
    <div className="kpi-card">
      <div className="card-icon">{icon}</div>
      <div className="card-content">
        <div className="card-title">{title}</div>
        <div className="card-value">{value}</div>
        {subtitle && <div className={`card-subtitle ${changeClass}`}>{subtitle}</div>}
      </div>
    </div>
  );
};

export default KpiCard;