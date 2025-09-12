// src/components/Header.js

import React from 'react';
import './Header.css';

// Mapeia as chaves de 'activeView' para títulos legíveis
const viewTitles = {
  general: 'Dashboard Geral',
  alerts: 'Alertas e Insights',
  market: 'Análise de Mercado',
  recommendations: 'Recomendações (IA)',
  debts: 'Análise de Dívidas',
  contracts: 'Gestão de Contratos',
};

// Adicionamos onFinancialsClick para abrir o novo modal
function Header({ company, activeView, onFinancialsClick }) {
  const title = viewTitles[activeView] || 'Dashboard';

  return (
    <header className="header">
      <div className="header-title">
        <h2>{title}</h2>
        <span>{company ? company.internal_alias : 'Nenhum cliente selecionado'}</span>
      </div>
      <div className="header-actions">
        {/* O botão só aparece se um cliente estiver selecionado */}
        {company && (
          <button className="btn" onClick={onFinancialsClick}>
            Informar Faturamento
          </button>
        )}
        <button className="btn btn-primary">Atualizar</button>
      </div>
    </header>
  );
}

export default Header;
