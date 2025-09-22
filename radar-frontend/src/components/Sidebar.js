// src/components/Sidebar.js

import React, { useState, useEffect, useCallback } from 'react';
import './Sidebar.css';

function Sidebar({ onCompanySelect, onViewChange, activeView, selectedCompany, onRegisterClick, refreshClients }) {
  const [clientes, setClientes] = useState([]);
  const [notifications, setNotifications] = useState({});
  const [error, setError] = useState(null);

  const fetchClientes = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/clientes');
      if (!response.ok) throw new Error('API de clientes falhou');
      const data = await response.json();
      setClientes(data);
      if (data.length > 0 && !selectedCompany) {
        onCompanySelect(data[0]);
      }
    } catch (err) {
      setError("Falha ao carregar clientes.");
      console.error(err);
    }
  }, [onCompanySelect, selectedCompany]);

  useEffect(() => {
    fetchClientes();
  }, [refreshClients, fetchClientes]);

  useEffect(() => {
    if (selectedCompany) {
      const fetchNotifications = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/sidebar/notifications/${selectedCompany.id}`);
          if (!response.ok) throw new Error('API de notificações falhou');
          const data = await response.json();
          setNotifications(data);
        } catch (err) {
          console.error("Erro ao buscar notificações:", err);
          setNotifications({});
        }
      };
      fetchNotifications();
    }
  }, [selectedCompany]);

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="unified-view">
          <span>VISÃO UNIFICADA</span>
          <p>RADAR OPTMUS</p>
          <span className="status-badge active">Ativa</span>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="section-header">
            <h4 className="section-title">CLIENTES</h4>
            <button className="add-client-btn" onClick={onRegisterClick}>+</button>
        </div>
        {error && <div className="error-message">{error}</div>}
        <div className="company-list">
            {clientes.map(cliente => (
              <div 
                key={cliente.id} 
                className={`company-item ${selectedCompany && selectedCompany.id === cliente.id ? 'selected' : ''}`}
                onClick={() => onCompanySelect(cliente)}
              >
                {cliente.internal_alias}
              </div>
            ))}
        </div>
      </div>

      <nav className="main-nav">
          <h4 className="section-title">ANÁLISE E ESTRATÉGIA</h4>
          <button onClick={() => onViewChange('general')} className={`nav-item ${activeView === 'general' ? 'active' : ''}`}>
            <span>Dashboard Geral</span>
            {notifications.dashboard > 0 && <span className="notification-badge">{notifications.dashboard}</span>}
          </button>
          <button onClick={() => onViewChange('alerts')} className={`nav-item ${activeView === 'alerts' ? 'active' : ''}`}>
            <span>Alertas e Insights</span>
          </button>
          <button onClick={() => onViewChange('market')} className={`nav-item ${activeView === 'market' ? 'active' : ''}`}>
            <span>Análise de Mercado</span>
          </button>
          <button onClick={() => onViewChange('recommendations')} className={`nav-item ${activeView === 'recommendations' ? 'active' : ''}`}>
            <span>Recomendações (IA)</span>
          </button>

          <h4 className="section-title">GESTÃO</h4>
          <button onClick={() => onViewChange('financials')} className={`nav-item ${activeView === 'financials' ? 'active' : ''}`}>
            <span>Financeiro</span>
          </button>
          <button onClick={() => onViewChange('debts')} className={`nav-item ${activeView === 'debts' ? 'active' : ''}`}>
            <span>Análise de Dívidas</span>
            {notifications.dividas > 0 && <span className="notification-badge error">{notifications.dividas}</span>}
          </button>
          <button onClick={() => onViewChange('contracts')} className={`nav-item ${activeView === 'contracts' ? 'active' : ''}`}>
            <span>Contratos</span>
            {notifications.contratos > 0 && <span className="notification-badge warning">{notifications.contratos}</span>}
          </button>
      </nav>
    </aside>
  );
}

export default Sidebar;