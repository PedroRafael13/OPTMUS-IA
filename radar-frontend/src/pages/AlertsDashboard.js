// src/pages/AlertsDashboard.js
import React, { useState, useEffect } from 'react';
import AlertCard from '../components/AlertCard';
// Se você não tiver este CSS, pode criá-lo ou remover a importação
// import './AlertsDashboard.css'; 

const AlertsDashboard = ({ company }) => {
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (company) {
      const fetchAlerts = async () => {
        setIsLoading(true);
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/alerts/${company.id}`);
          const data = await response.json();
          setAlerts(data);
        } catch (error) {
          console.error("Erro ao buscar alertas:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchAlerts();
    }
  }, [company]);

  if (isLoading) return <p>Carregando alertas...</p>;

  return (
    <div className="alerts-grid">
      {alerts.length > 0 ? (
        alerts.map(alert => <AlertCard key={alert.id} {...alert} />)
      ) : (
        <p>Nenhum alerta ou insight importante no momento.</p>
      )}
    </div>
  );
};

export default AlertsDashboard;