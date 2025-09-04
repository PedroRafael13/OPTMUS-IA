// src/components/Sidebar.js

import React, { useState, useEffect } from 'react';
import './Sidebar.css';

function Sidebar({ onCompanySelect, onViewChange, activeView, selectedCompany }) {
  const [clientes, setClientes] = useState([]);
  const [notifications, setNotifications] = useState({});
  const [error, setError] = useState(null);

  // Efeito para buscar a lista de clientes (roda apenas uma vez)
  useEffect(() => {
    const fetchClientes = async () => {
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
    };
    fetchClientes();
  }, [onCompanySelect, selectedCompany]);

  // Efeito para buscar as notificações (roda sempre que um novo cliente é selecionado)
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
          <p>Consolidado</p>
          <span className="status-badge active">Ativa</span>
        </div>
      </div>

      <div className="sidebar-section">
        <h4 className="section-title">CLIENTES</h4>
        {error && <div className="error-message">{error}</div>}
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

      <nav className="main-nav">
          <h4 className="section-title">ANÁLISE E ESTRATÉGIA</h4>
          <a href="#" onClick={() => onViewChange('general')} className={`nav-item ${activeView === 'general' ? 'active' : ''}`}>
            Dashboard Geral
            {notifications.dashboard > 0 && <span className="notification-badge">{notifications.dashboard}</span>}
          </a>
          <a href="#" onClick={() => onViewChange('alerts')} className={`nav-item ${activeView === 'alerts' ? 'active' : ''}`}>Alertas e Insights</a>
          <a href="#" onClick={() => onViewChange('debts')} className={`nav-item ${activeView === 'debts' ? 'active' : ''}`}>
            Análise de Dívidas
            {notifications.dividas > 0 && <span className="notification-badge error">{notifications.dividas}</span>}
          </a>
          {/* Adicione os outros links aqui, como Mercado e Benchmarking */}

          <h4 className="section-title">GESTÃO</h4>
          <a href="#" className="nav-item">
            Contratos
            {notifications.contratos > 0 && <span className="notification-badge warning">{notifications.contratos}</span>}
          </a>
          <a href="#" className="nav-item">Financeiro</a>
          <a href="#" className="nav-item">Recomendações</a>
      </nav>
    </aside>
  );
}

export default Sidebar;