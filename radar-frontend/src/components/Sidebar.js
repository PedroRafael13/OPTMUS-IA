// src/components/Sidebar.js

import React, { useState, useEffect, useCallback } from 'react';
import './Sidebar.css';

const API_URL = process.env.REACT_APP_API_URL;

// O componente agora recebe a nova prop 'onCompanyDelete'
function Sidebar({ onCompanySelect, onViewChange, activeView, selectedCompany, onRegisterClick, refreshClients, onCompanyDelete }) {
  const [clientes, setClientes] = useState([]);
  const [notifications, setNotifications] = useState({});
  const [error, setError] = useState(null);

  const fetchClientes = useCallback(async () => {
    try {
      // Usamos 'no-store' para garantir que a lista de clientes esteja sempre atualizada
      const response = await fetch(`${API_URL}/api/clientes`, { cache: 'no-store' });
      if (!response.ok) throw new Error('API de clientes falhou');
      const data = await response.json();
      setClientes(data);
      
      // Lógica para auto-selecionar o primeiro cliente, se nenhum estiver selecionado
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
          const response = await fetch(`${API_URL}/api/sidebar/notifications/${selectedCompany.id}`, { cache: 'no-store' });
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

  // NOVA FUNÇÃO para lidar com a exclusão de um cliente
  const handleDelete = async (companyToDelete) => {
    // Pede confirmação antes de uma ação destrutiva
    if (window.confirm(`Tem certeza que deseja excluir "${companyToDelete.internal_alias}"? Todos os dados associados (contratos, dívidas, etc.) serão perdidos permanentemente.`)) {
      try {
        const response = await fetch(`${API_URL}/api/clientes/${companyToDelete.id}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          // Em caso de sucesso, notifica o componente pai (App.js)
          onCompanyDelete(companyToDelete.id);
        } else {
          alert('Falha ao excluir o cliente.');
        }
      } catch (error) {
        console.error("Erro ao excluir cliente:", error);
        alert('Erro de conexão ao tentar excluir o cliente.');
      }
    }
  };

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
                {/* O nome do cliente agora está em um span para melhor alinhamento */}
                <span className="company-name">{cliente.internal_alias}</span>

                {/* Botão de exclusão adicionado aqui */}
                <button 
                  className="delete-client-btn" 
                  onClick={(e) => {
                    // e.stopPropagation() impede que o clique no botão dispare o onClick do div pai (que seleciona o cliente)
                    e.stopPropagation(); 
                    handleDelete(cliente);
                  }}
                >
                  &times; {/* Símbolo de "x" para fechar/excluir */}
                </button>
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
            <span>Análise de Concorrentes</span>
          </button>
          <button onClick={() => onViewChange('recommendations')} className={`nav-item ${activeView === 'recommendations' ? 'active' : ''}`}>
            <span>Recomendações (IA)</span>
          </button>

          <h4 className="section-title">GESTÃO</h4>
           <button onClick={() => onViewChange('billing')} className={`nav-item ${activeView === 'billing' ? 'active' : ''}`}>
            <span>Faturamento</span>
          </button>
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
          <button onClick={() => onViewChange('panel')} className={`nav-item ${activeView === 'panel' ? 'active' : ''}`}
            ><span>Painel de Dados</span>
          </button>
      </nav>
    </aside>
  );
}

export default Sidebar;