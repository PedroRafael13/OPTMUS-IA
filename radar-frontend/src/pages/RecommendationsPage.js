import React, { useState, useEffect } from 'react';
import './RecommendationsPage.css';

const RecommendationsPage = ({ company }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/recomendacoes/${company.id}`);
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error("Erro ao buscar recomendações:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (company) {
      fetchRecommendations();
    }
  }, [company]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/recomendacoes/${company.id}/gerar`, {
        method: 'POST',
      });
      if (response.ok) {
        alert('Novas recomendações geradas com sucesso!');
        fetchRecommendations(); // Re-fetch para exibir as novas
      } else {
        alert('Falha ao gerar novas recomendações.');
      }
    } catch (error) {
      console.error("Erro ao gerar recomendações:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getPriorityClass = (priority) => {
    if (priority === 'alta') return 'priority-high';
    if (priority === 'media') return 'priority-medium';
    return 'priority-low';
  };

  if (isLoading) return <p>Carregando recomendações...</p>;

  return (
    <div className="recommendations-page">
      <div className="recommendations-header">
        <h3>Recomendações Estratégicas (IA)</h3>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? 'Gerando...' : 'Gerar Novas Recomendações'}
        </button>
      </div>
      <div className="recommendations-grid">
        {recommendations.length > 0 ? (
          recommendations.map(rec => (
            <div key={rec.id} className="rec-card">
              <div className="rec-card-header">
                <h4>{rec.title}</h4>
                <span className={`priority-badge ${getPriorityClass(rec.priority)}`}>{rec.priority}</span>
              </div>
              <p>{rec.description}</p>
              <div className="rec-card-footer">
                <span><strong>Investimento:</strong> R$ {rec.investment.toLocaleString()}</span>
                <span><strong>ROI:</strong> {rec.roi}%</span>
                <span><strong>Prazo:</strong> {rec.timeline} meses</span>
              </div>
            </div>
          ))
        ) : (
          <p>Nenhuma recomendação disponível. Clique em "Gerar Novas Recomendações" para começar.</p>
        )}
      </div>
    </div>
  );
};

export default RecommendationsPage;