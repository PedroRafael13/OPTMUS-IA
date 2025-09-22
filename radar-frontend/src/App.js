// src/App.js

import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Modal from './components/Modal';
import RegisterClientForm from './components/RegisterClientForm';
import FinancialDataForm from './components/FinancialDataForm';

// Importação das páginas
import GeneralDashboard from './pages/GeneralDashboard';
import AlertsDashboard from './pages/AlertsDashboard';
import DebtAnalysisPage from './pages/DebtAnalysisPage';
import ContractsPage from './pages/ContractsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import MarketPage from './pages/MarketPage';
import FinancialDashboardPage from './pages/FinancialDashboardPage';


import './App.css';

// Placeholder para futuras páginas
const BenchmarkingPage = () => <h2>Página de Benchmarking (Em construção)</h2>;

function App() {
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [activeView, setActiveView] = useState('general');
  
  // Controle centralizado de modais: 'register', 'financials', ou null
  const [modalContent, setModalContent] = useState(null); 

  // Estado para forçar a atualização da lista de clientes no Sidebar
  const [refreshClients, setRefreshClients] = useState(false);

  // Função chamada quando o formulário de registro é enviado com sucesso
  const handleRegisterSuccess = () => {
    setModalContent(null); // Fecha o modal
    setRefreshClients(prev => !prev); // Alterna o valor para disparar o useEffect no Sidebar
  };
  
  // Função chamada quando o formulário de dados financeiros é enviado com sucesso
  const handleFinancialsSuccess = (updatedData) => {
    // Atualiza o objeto do cliente com os novos dados financeiros
    setSelectedCompany(prev => ({ ...prev, ...updatedData }));
    setModalContent(null); // Fecha o modal
  };

  // Função para renderizar a página correta com base no estado 'activeView'
  const renderActiveView = () => {
    // Se nenhum cliente foi selecionado ainda, mostra uma mensagem inicial
    if (!selectedCompany) {
      return (
        <div className="initial-message">
          <h2>Bem-vindo ao RADAR OPTMUS</h2>
          <p>Selecione um cliente na barra lateral ou cadastre um novo para começar.</p>
        </div>
      );
    }
    // Usa um switch para determinar qual componente de página renderizar
    switch (activeView) {
      case 'general': return <GeneralDashboard company={selectedCompany} />;
      case 'alerts': return <AlertsDashboard company={selectedCompany} />;
      case 'debts': return <DebtAnalysisPage company={selectedCompany} />;
      case 'contracts': return <ContractsPage company={selectedCompany} />;
      case 'recommendations': return <RecommendationsPage company={selectedCompany} />;
      case 'market': return <MarketPage company={selectedCompany} onAnalysisComplete={setSelectedCompany} />;
      case 'financials': return <FinancialDashboardPage company={selectedCompany} />;
      case 'benchmarking': return <BenchmarkingPage />;
      default: return <GeneralDashboard company={selectedCompany} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar 
        selectedCompany={selectedCompany} 
        onCompanySelect={setSelectedCompany} 
        onViewChange={setActiveView} 
        activeView={activeView}
        onRegisterClick={() => setModalContent('register')}
        refreshClients={refreshClients}
      />
      
      <main className="main-content">
        <Header 
            company={selectedCompany} 
            activeView={activeView}
            onFinancialsClick={() => setModalContent('financials')}
        />
        <div className="dashboard-area">
          {renderActiveView()}
        </div>
      </main>

      {/* Renderização do Modal de forma condicional */}
      <Modal show={!!modalContent} onClose={() => setModalContent(null)}>
        {modalContent === 'register' && (
          <RegisterClientForm 
            onSuccess={handleRegisterSuccess}
            onCancel={() => setModalContent(null)}
          />
        )}
        {modalContent === 'financials' && selectedCompany && (
          <FinancialDataForm
            company={selectedCompany}
            onSuccess={handleFinancialsSuccess}
            onCancel={() => setModalContent(null)}
          />
        )}
      </Modal>
    </div>
  );
}

export default App;