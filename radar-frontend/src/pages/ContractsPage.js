// src/pages/ContractsPage.js

import React, { useState, useEffect, useCallback } from 'react';
import KpiCard from '../components/KpiCard'; // Importe o KpiCard
import AlertCard from '../components/AlertCard'; // Importe o AlertCard
import './ContractsPage.css';

const API_URL = process.env.REACT_APP_API_URL;

const ContractsPage = ({ company }) => {
  // Estados para armazenar os dados da nova API
  const [kpis, setKpis] = useState(null);
  const [contracts, setContracts] = useState([]);
  const [insights, setInsights] = useState([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    service: '',
    price: '',
    responsible: '',
    due_date: ''
  });

  // Função de busca de dados atualizada para o novo formato da API
  const fetchContractData = useCallback(async () => {
    if (!company) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/contratos/cliente/${company.id}`);
      if (!response.ok) {
        throw new Error('Falha ao buscar os dados dos contratos.');
      }
      const data = await response.json();

      // Atualiza os estados com os dados recebidos da API
      setKpis(data.kpis || {});
      setContracts(data.contracts || []);
      setInsights(data.insights || []);

    } catch (err) {
      console.error("Erro ao buscar dados dos contratos:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [company]);

  useEffect(() => {
    fetchContractData();
  }, [fetchContractData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/contratos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, company_id: company.id, price: parseFloat(formData.price) })
      });
      if (response.ok) {
        alert('Contrato adicionado com sucesso!');
        setShowForm(false);
        setFormData({ service: '', price: '', responsible: '', due_date: '' }); // Limpa o formulário
        fetchContractData(); // Re-busca todos os dados para atualizar a tela
      } else {
        alert('Falha ao adicionar contrato.');
      }
    } catch (error) {
      console.error("Erro ao adicionar contrato:", error);
    }
  };

  // Função auxiliar para formatar valores monetários
  const formatBRL = (value = 0) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  if (isLoading) return <p>Carregando painel de contratos...</p>;
  if (error) return <p>Erro ao carregar dados: {error}</p>;

  return (
    <div className="contracts-page">
      {/* SEÇÃO DE KPIs ESTRATÉGICOS */}
      <div className="kpi-grid">
        <KpiCard title="MRR Ativo (Receita Recorrente)" value={formatBRL(kpis.mrr)} />
        <KpiCard title="Vencendo em 60 dias" value={kpis.expiring_soon_count} />
        <KpiCard title="Risco de Concentração" value={`${(kpis.concentration_risk || 0).toFixed(1)}%`} subtitle="No maior contrato" />
      </div>

      <div className="contracts-header">
        <h3>Contratos Ativos ({contracts.length})</h3>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : 'Adicionar Contrato'}
        </button>
      </div>

      {showForm && (
        <div className="contract-form-container">
          <form onSubmit={handleSubmit}>
            <input name="service" value={formData.service} onChange={handleInputChange} placeholder="Descrição do Serviço" required />
            <input name="price" type="number" step="0.01" value={formData.price} onChange={handleInputChange} placeholder="Preço Mensal (ex: 4500.00)" required />
            <input name="responsible" value={formData.responsible} onChange={handleInputChange} placeholder="Responsável" />
            <input name="due_date" type="date" value={formData.due_date} onChange={handleInputChange} required />
            <button type="submit">Salvar Contrato</button>
          </form>
        </div>
      )}

      {/* TABELA DE CONTRATOS APRIMORADA */}
      <div className="contracts-list">
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Serviço</th>
              <th>Preço Mensal</th>
              <th>Responsável</th>
              <th>Vencimento</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {contracts.map(contract => (
              <tr key={contract.contract_id}>
                <td>
                  <span className={`status-badge status-${(contract.status || 'default').toLowerCase()}`}>
                    {contract.status}
                  </span>
                </td>
                <td>{contract.service_description}</td>
                <td>{formatBRL(contract.monthly_price)}</td>
                <td>{contract.responsible_person}</td>
                <td>{new Date(contract.due_date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })}</td>
                <td>
                  <div className="action-buttons">
                    {/* Espaço para futuros botões de ação */}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* SEÇÃO DE INSIGHTS DO AGENTE */}
      {insights && insights.length > 0 && (
        <div className="agent-insights-section">
          <h3>Insights do Agente</h3>
          <div className="alerts-grid">
            {insights.map((insight, index) => (
              <AlertCard key={index} icon={insight.icon} title={insight.title} description={insight.description} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractsPage;