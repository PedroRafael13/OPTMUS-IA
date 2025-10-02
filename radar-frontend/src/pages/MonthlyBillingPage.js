// src/pages/MonthlyBillingPage.js

import React, { useState, useEffect, useCallback } from 'react';
import KpiCard from '../components/KpiCard';
import AlertCard from '../components/AlertCard';
import './MonthlyBillingPage.css';

const API_URL = process.env.REACT_APP_API_URL;

const MonthlyBillingPage = ({ company }) => {
  // Estados para armazenar a nova estrutura de dados do agente
  const [kpis, setKpis] = useState(null);
  const [billingItems, setBillingItems] = useState([]);
  const [agentActions, setAgentActions] = useState([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBillingData = useCallback(async () => {
    if (!company) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/financeiro/billing/${company.id}`);
      if (!response.ok) throw new Error('Falha ao buscar dados de faturamento.');
      
      const data = await response.json();
      setKpis(data.kpis || {});
      setBillingItems(data.billing_items || []);
      setAgentActions(data.agent_actions || []);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [company]);

  useEffect(() => {
    fetchBillingData();
  }, [fetchBillingData]);

  const handleMarkAsPaid = async (item) => {
    if (item.is_paid) return;

    // Desabilita o botão temporariamente para evitar cliques duplos
    setBillingItems(currentItems => 
        currentItems.map(c => c.contract_id === item.contract_id ? { ...c, isDisabled: true } : c)
    );

    try {
      const response = await fetch(`${API_URL}/api/financeiro/billing/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contract_id: item.contract_id,
          company_id: item.company_id,
          amount: item.monthly_price
        })
      });
      if (!response.ok) throw new Error('Falha ao registrar pagamento.');
      // Recarrega todos os dados para atualizar a tela inteira (KPIs, tabela, insights)
      fetchBillingData();
    } catch (err) {
      alert(err.message);
      // Reabilita o botão em caso de erro
      setBillingItems(currentItems => 
        currentItems.map(c => c.contract_id === item.contract_id ? { ...c, isDisabled: false } : c)
      );
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'Pago': return 'status-paid';
      case 'Em Atraso': return 'status-overdue';
      case 'Pendente':
      default:
        return 'status-pending';
    }
  };

  const formatBRL = (value = 0) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  if (isLoading) return <p>Agente de cobrança analisando o faturamento...</p>;
  if (error) return <p>Erro: {error}</p>;

  return (
    <div className="billing-page">
      <div className="page-header">
        <h3>Painel de Faturamento e Cobrança ({new Date().toLocaleString('pt-BR', { month: 'long' })})</h3>
      </div>
      
      {/* SEÇÃO DE KPIs */}
      {kpis && (
        <div className="kpi-grid">
            <KpiCard title="Faturamento Total" value={formatBRL(kpis.total_billing)} />
            <KpiCard title="Total Recebido" value={formatBRL(kpis.total_received)} />
            <KpiCard title="Inadimplência (Pendente)" value={formatBRL(kpis.total_pending)} />
            <KpiCard title="Taxa de Inadimplência" value={`${(kpis.pending_rate || 0).toFixed(1)}%`} />
        </div>
      )}

      {/* TABELA APRIMORADA */}
      <div className="billing-table-container">
        <table>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Serviço</th>
              <th>Valor (R$)</th>
              <th>Status</th>
              <th>Dias em Atraso</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {billingItems.map(item => (
              <tr key={item.contract_id}>
                <td>{item.company_name}</td>
                <td>{item.service_description}</td>
                <td>{item.monthly_price.toFixed(2)}</td>
                <td>
                  <span className={getStatusClass(item.status)}>{item.status}</span>
                </td>
                <td>{item.days_overdue > 0 ? item.days_overdue : '-'}</td>
                <td>
                  <button 
                    className={`btn-action ${item.status === 'Em Atraso' ? 'btn-collect' : 'btn-pay'}`}
                    disabled={item.is_paid || item.isDisabled}
                    onClick={() => handleMarkAsPaid(item)}
                  >
                    {item.is_paid ? 'Registrado' : (item.status === 'Em Atraso' ? 'Iniciar Cobrança' : 'Registrar Pagamento')}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* SEÇÃO DE AÇÕES DO AGENTE */}
      {agentActions && agentActions.length > 0 && (
         <div className="agent-insights-section">
          <h3>Ações do Agente de Cobrança</h3>
          <div className="alerts-grid">
            {agentActions.map((action, index) => (
              <AlertCard key={index} icon="💡" title={action.title} description={action.description} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MonthlyBillingPage;