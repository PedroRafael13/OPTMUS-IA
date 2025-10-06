// src/pages/RecommendationsPage.js

import React, { useState, useEffect, useCallback } from 'react';
import Modal from '../components/Modal';
import GenerateRecsForm from '../components/GenerateRecsForm';
import './RecommendationsPage.css';

const API_URL = process.env.REACT_APP_API_URL;

const RecommendationsPage = ({ company }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchRecommendations = useCallback(async () => {
    if (!company) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/recomendacoes/${company.id}`);
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error("Erro ao buscar recomendações:", error);
    } finally {
      setIsLoading(false);
    }
  }, [company]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  const handleGenerateSubmit = async (formData) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/recomendacoes/${company.id}/gerar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        setIsModalOpen(false);
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

  const handleClear = async () => {
    if (window.confirm("Tem certeza que deseja limpar todas as recomendações para este cliente?")) {
      try {
        const response = await fetch(`${API_URL}/api/recomendacoes/${company.id}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setRecommendations([]);
          alert('Recomendações excluídas com sucesso.');
        } else {
          alert('Falha ao excluir recomendações.');
        }
      } catch (error) {
        console.error("Erro ao excluir recomendações:", error);
      }
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
        <div className="header-actions">
          {recommendations.length > 0 && (
            <button className="btn btn-secondary" onClick={handleClear}>
              Limpar Sugestões
            </button>
          )}
          <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
            Gerar Novas Recomendações
          </button>
        </div>
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
                <span><strong>Invest.:</strong> R$ {(rec.investment || 0).toLocaleString()}</span>
                <span><strong>ROI:</strong> {rec.roi || 0}%</span>
                <span><strong>Prazo:</strong> {rec.timeline || 0} meses</span>
              </div>
            </div>
          ))
        ) : (
          <div className="no-recommendations">
            <p>Nenhuma recomendação disponível.</p>
            <p>Clique em "Gerar Novas Recomendações" para começar.</p>
          </div>
        )}
      </div>

      <Modal show={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <GenerateRecsForm 
            onSubmit={handleGenerateSubmit} 
            onCancel={() => setIsModalOpen(false)}
            isGenerating={isGenerating}
        />
      </Modal>
    </div>
  );
};

export default RecommendationsPage;