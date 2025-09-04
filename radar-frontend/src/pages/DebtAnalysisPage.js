// src/pages/DebtAnalysisPage.js
import React, { useState, useEffect } from 'react';
import KpiCard from '../components/KpiCard';
import AlertCard from '../components/AlertCard';
// Se você não tiver este CSS, pode criá-lo ou remover a importação
// import './DebtAnalysisPage.css';

const DebtAnalysisPage = ({ company }) => {
  const [debtData, setDebtData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (company) {
      const fetchDebtData = async () => {
        setIsLoading(true);
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/debts/${company.id}`);
          const data = await response.json();
          setDebtData(data);
        } catch (error) {
          console.error("Erro ao buscar dados de dívidas:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchDebtData();
    }
  }, [company]);

  if (isLoading) return <p>Carregando análise de dívidas...</p>;
  if (!debtData) return <p>Não foi possível carregar os dados.</p>;

  const { totals, strategic_analysis, details } = debtData;

  return (
    <div className="debt-analysis-page">
      <div className="kpi-grid">
        <KpiCard title="Total de Dívidas" value={`R$ ${(totals.total_dividas / 1000).toFixed(1)}K`} />
        <KpiCard title="Dívidas Bancárias" value={`R$ ${(totals.total_bancario / 1000).toFixed(1)}K`} />
        <KpiCard title="Fornecedores" value={`R$ ${(totals.total_fornecedor / 1000).toFixed(1)}K`} />
        <KpiCard title="Protestos" value={`R$ ${(totals.total_protestos / 1000).toFixed(1)}K`} />
      </div>
      <div className="strategic-section">
        <h3>Análise Estratégica</h3>
        <div className="alerts-grid">
          <AlertCard icon="⚠️" title="Score Crítico" description={strategic_analysis.score_critico} />
          {strategic_analysis.oportunidade && <AlertCard icon="💰" title="Oportunidade de Negociação" description={strategic_analysis.oportunidade} />}
        </div>
      </div>
    </div>
  );
};

export default DebtAnalysisPage;