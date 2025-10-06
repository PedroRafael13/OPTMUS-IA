// src/pages/MarketAnalysisPage.js

import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './MarketAnalysisPage.css';

const API_URL = process.env.REACT_APP_API_URL;

const MarketAnalysisPage = ({ company }) => {
  const [competitors, setCompetitors] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newCompetitor, setNewCompetitor] = useState({ name: '', location: '', revenue: '' });
  
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedAI, setSelectedAI] = useState('gemini');

  const fetchCompetitors = useCallback(async () => {
    if (!company) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/competitors/${company.id}`);
      const data = await response.json();
      setCompetitors(data);
    } catch (error) {
      console.error("Erro ao buscar concorrentes:", error);
    } finally {
      setIsLoading(false);
    }
  }, [company]);

  useEffect(() => {
    fetchCompetitors();
  }, [fetchCompetitors]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCompetitor(prev => ({ ...prev, [name]: value }));
  };

  const handleAddCompetitor = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/competitors/${company.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newCompetitor, revenue: parseFloat(newCompetitor.revenue) })
      });
      if (response.ok) {
        setNewCompetitor({ name: '', location: '', revenue: '' });
        fetchCompetitors();
      }
    } catch (error) {
      console.error("Erro ao adicionar concorrente:", error);
    }
  };

  const handleDeleteCompetitor = async (id) => {
    try {
      await fetch(`${API_URL}/api/competitors/delete/${id}`, { method: 'DELETE' });
      fetchCompetitors();
    } catch (error) {
      console.error("Erro ao excluir concorrente:", error);
    }
  };
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/api/competitors/${company.id}/upload_csv`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        alert('CSV importado com sucesso!');
        fetchCompetitors();
      } else {
        const data = await response.json();
        alert(`Erro: ${data.error}`);
      }
    } catch (error) {
      console.error('Erro no upload do CSV:', error);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const newHistory = [...chatHistory, { role: 'user', content: chatInput }];
    setChatHistory(newHistory);
    setChatInput('');
    setIsChatLoading(true);

    try {
        const response = await fetch(`${API_URL}/api/analysis/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: chatInput, model: selectedAI })
        });
        const data = await response.json();
        setChatHistory(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (error) {
        setChatHistory(prev => [...prev, { role: 'ai', content: 'Erro ao conectar com a IA.' }]);
    } finally {
        setIsChatLoading(false);
    }
  };

  const chartData = [
    { name: company.internal_alias, Receita: company.annual_revenue || 0 },
    ...competitors.map(c => ({ name: c.name, Receita: c.revenue }))
  ];

  return (
    <div className="market-page">
      <div className="column">
        {/* Card de Gestão de Concorrentes */}
        <div className="card">
          <div className="card-header">
            <h3>Gestão de Concorrentes</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleAddCompetitor} className="competitor-form">
              <input name="name" value={newCompetitor.name} onChange={handleInputChange} placeholder="Nome do Concorrente" required />
              <input name="location" value={newCompetitor.location} onChange={handleInputChange} placeholder="Localização" required />
              <input name="revenue" type="number" value={newCompetitor.revenue} onChange={handleInputChange} placeholder="Receita Anual" required />
              <button type="submit">Adicionar</button>
            </form>

            <hr className="form-separator" />
            
            <div className="csv-import">
              <label htmlFor="csv-upload" className="csv-label">Importar via CSV</label>
              <input id="csv-upload" type="file" accept=".csv" onChange={handleFileUpload} />
              <small>Formato: nome,localizacao,receita (sem cabeçalho)</small>
            </div>
            
            <div className="competitor-list">
              {isLoading ? <p>Carregando...</p> : competitors.map(c => (
                <div key={c.id} className="competitor-item">
                  <span><strong>{c.name}</strong> ({c.location}) - R$ {c.revenue.toLocaleString()}</span>
                  <button onClick={() => handleDeleteCompetitor(c.id)}>×</button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Card de Gráfico Comparativo */}
        <div className="card">
            <div className="card-header">
              <h3>Comparativo de Receita</h3>
            </div>
            <div className="card-body">
              <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis tickFormatter={(val) => `R$${(val/1000)}k`} />
                      <Tooltip formatter={(val) => `R$ ${val.toLocaleString()}`} />
                      <Legend />
                      <Bar dataKey="Receita" fill="#8884d8" />
                  </BarChart>
              </ResponsiveContainer>
            </div>
        </div>
      </div>
      
      <div className="column">
        {/* Card do Chat com IA */}
        <div className="card">
          <div className="card-header">
            <h3>Assistente de Estratégia IA</h3>
          </div>
          <div className="card-body">
            <div className="ai-selector">
              <button className={selectedAI === 'gemini' ? 'active' : ''} onClick={() => setSelectedAI('gemini')}>Gemini</button>
              <button className={selectedAI === 'gpt' ? 'active' : ''} onClick={() => setSelectedAI('gpt')}>GPT-4</button>
            </div>
            <div className="chat-box">
              <div className="chat-history">
                {chatHistory.length === 0 && !isChatLoading && (
                  <div className="chat-empty-state">
                    <div className="empty-state-icon">🧠</div>
                    <h4>Assistente de Estratégia</h4>
                    <p>Faça uma pergunta para começar.</p>
                    <div className="suggestion-buttons">
                      <button onClick={() => setChatInput('Qual o ponto fraco do meu principal concorrente?')}>Ponto fraco do concorrente</button>
                      <button onClick={() => setChatInput('Sugira uma nova estratégia de preço')}>Estratégia de preço</button>
                      <button onClick={() => setChatInput('Quais tendências devo observar neste mercado?')}>Tendências de mercado</button>
                    </div>
                  </div>
                )}
                {chatHistory.map((msg, index) => (
                  <div key={index} className={`chat-message ${msg.role}`}>
                    <p>{msg.content}</p>
                  </div>
                ))}
                {isChatLoading && <div className="chat-message ai"><p>Pensando...</p></div>}
              </div>
              <form onSubmit={handleChatSubmit} className="chat-input-form">
                <input value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder="Pergunte algo sobre o mercado..." />
                <button type="submit">Enviar</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysisPage;