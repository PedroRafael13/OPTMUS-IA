import React, { useState } from 'react';
import KpiCard from '../components/KpiCard'; // Reutilize o KpiCard
import './MarketPage.css';

const MarketPage = ({ company, onAnalysisComplete }) => {
    // Começa com os dados do company prop, mas pode ser atualizado
  const [analysisData, setAnalysisData] = useState({
    market_share: company.market_share,
    market_rank: company.market_rank,
    // Adicione outros dados se a API retornar
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleRunAnalysis = async () => {
    if (!company.annual_revenue) {
        alert('Erro: O faturamento anual do cliente precisa ser informado para realizar a análise de mercado.');
        return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/mercado/analise/${company.id}`, {
        method: 'POST',
      });
      const data = await response.json();
      if (response.ok) {
        setAnalysisData(data); // Atualiza a página com os novos dados
        // Opcional: Chamar uma função para atualizar o estado global do cliente
        // onAnalysisComplete(data);
      } else {
        alert(`Falha ao analisar: ${data.error}`);
      }
    } catch (error) {
      console.error("Erro ao rodar análise de mercado:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="market-analysis-page">
      <div className="market-header">
        <h3>Análise de Mercado</h3>
        <button className="btn btn-primary" onClick={handleRunAnalysis} disabled={isLoading}>
          {isLoading ? 'Analisando...' : 'Rodar Nova Análise'}
        </button>
      </div>

      <div className="kpi-grid">
        <KpiCard title="Market Share" value={`${(analysisData.market_share || 0).toFixed(2)}%`} />
        <KpiCard title="Posição no Ranking" value={`#${analysisData.market_rank || 'N/A'}`} subtitle={`de ${analysisData.total_companies || '?'} empresas`} />
        <KpiCard title="Mercado Total (Estimado)" value={`R$ ${( (analysisData.total_market_size || 0) / 1000000).toFixed(1)}M`} />
        <KpiCard title="Potencial de Captura" value={`R$ ${((analysisData.potential_capture || 0) / 1000).toFixed(1)}K`} />
      </div>

      {analysisData.qualitative_analysis && (
        <div className="insights-section">
            <h3>Insights Estratégicos</h3>
            <ul>
                <li><strong>Crescimento do Mercado:</strong> {analysisData.qualitative_analysis.crescimento_mercado}</li>
                <li><strong>Oportunidade Geográfica:</strong> {analysisData.qualitative_analysis.oportunidade_geografica}</li>
                <li><strong>Posição Competitiva:</strong> {analysisData.qualitative_analysis.posicao_competitiva}</li>
                <li><strong>Pressão Competitiva:</strong> {analysisData.qualitative_analysis.pressao_competitiva}</li>
            </ul>
        </div>
      )}
    </div>
  );
};

export default MarketPage;