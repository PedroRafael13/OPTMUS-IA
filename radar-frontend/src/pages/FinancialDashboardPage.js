// src/pages/FinancialDashboardPage.js

import React, { useState, useEffect } from 'react';
import KpiCard from '../components/KpiCard';
import AlertCard from '../components/AlertCard';
import CashFlowChart from '../components/CashFlowChart';
import './DebtAnalysisPage.css'; // Reutilizando estilos

const FinancialDashboardPage = ({ company }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (company) {
      const fetchData = async () => {
        setIsLoading(true);
        setError(null); // Limpa erros anteriores
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/financeiro/dashboard/${company.id}`);
          const data = await response.json();

          if (!response.ok || data.error) {
            throw new Error(data.error || 'Falha ao buscar dados financeiros.');
          }
          
          setDashboardData(data);
        } catch (err) {
          console.error("Erro ao buscar dados financeiros:", err);
          setError(err.message);
        } finally {
          setIsLoading(false);
        }
      };
      fetchData();
    }
  }, [company]);

  // Exibe a mensagem de carregamento
  if (isLoading) {
    return <p>Carregando dashboard financeiro...</p>;
  }

  // Exibe a mensagem de erro se a API falhou
  if (error) {
    return <p>Erro ao carregar os dados: {error}</p>;
  }

  // Garante que os dados existem antes de tentar usá-los
  if (!dashboardData || !dashboardData.kpis) {
    return <p>Não foi possível carregar os dados do dashboard.</p>;
  }

  const { kpis, qualitative_analysis, projection_chart_data } = dashboardData;
  const formatBRL = (value) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="debt-analysis-page"> {/* Reutilizando classe principal */}
        <div className="page-header">
            <h3>Dashboard Financeiro</h3>
        </div>

        <div className="kpi-grid">
            <KpiCard title="Receita Bruta (30d)" value={formatBRL(kpis.receita_bruta)} />
            <KpiCard title="Despesas Totais (30d)" value={formatBRL(kpis.despesas_totais)} />
            <KpiCard title="Margem Líquida (30d)" value={formatBRL(kpis.margem_liquida)} />
            <KpiCard title="Fluxo Líquido (30d)" value={formatBRL(kpis.fluxo_liquido)} />
        </div>

        <CashFlowChart data={projection_chart_data} />

        <div className="strategic-section">
            <h3>Análise e Insights</h3>
            <div className='alerts-grid'>
            {qualitative_analysis && Object.entries(qualitative_analysis).map(([key, value]) => (
                <AlertCard key={key} icon="💡" title={key.replace(/_/g, ' ')} description={value} />
            ))}
            </div>
        </div>
    </div>
  );
};

export default FinancialDashboardPage;