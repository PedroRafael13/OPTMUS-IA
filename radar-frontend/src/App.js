// src/App.js

import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// Importação das "páginas" principais que já criamos
import GeneralDashboard from './pages/GeneralDashboard';
import AlertsDashboard from './pages/AlertsDashboard';
import DebtAnalysisPage from './pages/DebtAnalysisPage';

// Placeholders para as futuras páginas, para a navegação funcionar sem erros
const ContractsPage = () => <h2>Página de Contratos (Em construção)</h2>;
const RecommendationsPage = () => <h2>Página de Recomendações (Em construção)</h2>;
const MarketPage = () => <h2>Página de Análise de Mercado (Em construção)</h2>;
const BenchmarkingPage = () => <h2>Página de Benchmarking (Em construção)</h2>;


import './App.css';

function App() {
  // Estado para guardar qual cliente está selecionado globalmente
  const [selectedCompany, setSelectedCompany] = useState(null);
  // Estado para controlar qual tela/view está ativa no painel principal
  const [activeView, setActiveView] = useState('general'); // A tela inicial é o Dashboard Geral

  // Função para renderizar a página correta com base no estado 'activeView'
  const renderActiveView = () => {
    // Se nenhum cliente foi selecionado ainda, mostra uma mensagem inicial
    if (!selectedCompany) {
      return <h2>Selecione um cliente na barra lateral para começar</h2>;
    }

    // Usa um switch para determinar qual componente de página renderizar
    switch (activeView) {
      case 'general':
        return <GeneralDashboard company={selectedCompany} />;
      case 'alerts':
        return <AlertsDashboard company={selectedCompany} />;
      case 'debts':
        return <DebtAnalysisPage company={selectedCompany} />;
      case 'contracts':
        return <ContractsPage />;
      case 'recommendations':
        return <RecommendationsPage />;
      case 'market':
        return <MarketPage />;
      case 'benchmarking':
        return <BenchmarkingPage />;
      default:
        // Por padrão, sempre volta para o Dashboard Geral
        return <GeneralDashboard company={selectedCompany} />;
    }
  };

  return (
    <div className="app-layout">
      {/* A Sidebar agora recebe 4 "props":
        - selectedCompany: Para saber qual cliente está ativo.
        - onCompanySelect: Para avisar o App.js quando um novo cliente for clicado.
        - onViewChange: Para avisar o App.js quando um link de navegação for clicado.
        - activeView: Para saber qual link de navegação deve ser destacado como "ativo".
      */}
      <Sidebar 
        selectedCompany={selectedCompany} 
        onCompanySelect={setSelectedCompany} 
        onViewChange={setActiveView} 
        activeView={activeView}
      />
      
      <main className="main-content">
        <Header company={selectedCompany} />
        <div className="dashboard-area">
          {renderActiveView()}
        </div>
      </main>
    </div>
  );
}

export default App;