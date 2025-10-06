// src/pages/GeneralDashboard.js

import React, { useState, useEffect } from 'react';
import KpiCard from '../components/KpiCard';
import RevenueChart from '../components/RevenueChart';
// Importe um novo CSS para este dashboard (você precisará criá-lo)
import './GeneralDashboard.css'; 

const API_URL = process.env.REACT_APP_API_URL;

// O componente agora recebe 'onViewChange' para a navegação
const GeneralDashboard = ({ company, onViewChange }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (company) {
      const fetchDashboardData = async () => {
        setIsLoading(true);
        setError(null);
        try {
          // A API agora retorna o objeto completo com a análise do agente
          const response = await fetch(`${API_URL}/api/dashboard/general/${company.id}`);
          if (!response.ok) {
            throw new Error('Falha ao buscar dados do dashboard.');
          }
          const data = await response.json();
          setDashboardData(data);
        } catch (err) {
          console.error("Erro ao buscar dados do dashboard:", err);
          setError(err.message);
        } finally {
          setIsLoading(false);
        }
      };
      fetchDashboardData();
    }
  }, [company]);

  if (isLoading) return <p>Agente analisando o dashboard...</p>;
  if (error) return <p>Erro ao carregar dashboard: {error}</p>;
  if (!dashboardData) return <p>Não foi possível carregar os dados do dashboard.</p>;

  // Desestruturando os dados recebidos da API
  const { kpis, revenue_evolution_data, agent_summary, recommended_actions } = dashboardData;
  
  // Função auxiliar para mapear prioridades para classes CSS
  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  };

  return (
    <div className="general-dashboard">
      {/* 1. Resumo do Agente */}
      {agent_summary && (
        <div className="agent-summary-card">
          <p><strong>Resumo do Agente:</strong> {agent_summary}</p>
        </div>
      )}

      {/* 2. Layout de Duas Colunas */}
      <div className="dashboard-layout">
        {/* Coluna Principal (Esquerda) */}
        <div className="main-column">
          <div className="kpi-grid">
            <KpiCard title="Receita Mensal" value={`R$ ${(kpis.monthly_revenue / 1000).toFixed(1)}K`} subtitle={`${(kpis.revenue_change_percent || 0).toFixed(1)}% vs período anterior`} change={kpis.revenue_change_percent} />
            <KpiCard title="Contratos Ativos" value={kpis.active_contracts} subtitle={`Ticket médio: R$ ${(kpis.average_ticket / 1000).toFixed(1)}K`} />
            <KpiCard title="Market Share" value={`${(kpis.market_share || 0).toFixed(2)}%`} subtitle={kpis.market_rank} />
            <KpiCard title="Crescimento (30d)" value={`${(kpis.revenue_change_percent || 0).toFixed(1)}%`} change={kpis.revenue_change_percent} />
          </div>
          <RevenueChart data={revenue_evolution_data} />
        </div>

        {/* Coluna do Agente (Direita) */}
        <div className="sidebar-column">
          <div className="card">
            <div className="card-header">
              <h3>Ações Recomendadas</h3>
            </div>
            <div className="card-body">
              {recommended_actions && recommended_actions.length > 0 ? (
                <ul className="action-list">
                  {recommended_actions.map(action => (
                    <li key={action.id} className="action-item">
                      <span className={`priority-tag ${getPriorityClass(action.priority)}`}>{action.priority.toUpperCase()}</span>
                      <div className="action-content">
                        <strong>{action.title}</strong>
                        <p>{action.description}</p>
                        <button className="btn btn-secondary" onClick={() => onViewChange(action.link)}>
                          {action.button_text}
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>Nenhuma ação urgente recomendada no momento. Bom trabalho!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeneralDashboard;