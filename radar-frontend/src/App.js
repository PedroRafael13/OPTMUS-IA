// src/App.js

import React, { useState } from 'react';

// Componentes principais da estrutura
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Modal from './components/Modal';

// Formulários para os Modais
import RegisterClientForm from './components/RegisterClientForm';
import FinancialDataForm from './components/FinancialDataForm';

// Páginas de conteúdo do Dashboard
import GeneralDashboard from './pages/GeneralDashboard';
import AlertsDashboard from './pages/AlertsDashboard';
import DebtAnalysisPage from './pages/DebtAnalysisPage';
import ContractsPage from './pages/ContractsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import MarketAnalysisPage from './pages/MarketAnalysisPage';
import MonthlyBillingPage from './pages/MonthlyBillingPage';
import FinancialDashboardPage from './pages/FinancialDashboardPage';

// Estilos
import './App.css';

function App() {
  // Estado para guardar qual cliente está selecionado globalmente
  const [selectedCompany, setSelectedCompany] = useState(null);
  // Estado para controlar qual tela/view está ativa no painel principal
  const [activeView, setActiveView] = useState('general');
  // Estado para controlar o conteúdo do modal (ex: 'register', 'financials', ou null)
  const [modalContent, setModalContent] = useState(null);
  // Estado para forçar a atualização da lista de clientes na Sidebar
  const [refreshClients, setRefreshClients] = useState(false);

  // Função chamada quando o formulário de registro é bem-sucedido
  const handleRegisterSuccess = () => {
    setModalContent(null); // Fecha o modal
    setRefreshClients(prev => !prev); // Ativa o gatilho para recarregar a lista de clientes
  };

  // Função chamada quando o formulário de dados financeiros é bem-sucedido
  const handleFinancialsSuccess = (updatedCompany) => {
    setSelectedCompany(updatedCompany); // Atualiza os dados do cliente selecionado
    setModalContent(null); // Fecha o modal
  };
  
  // Função para lidar com a exclusão de um cliente
  const handleCompanyDeleted = (deletedCompanyId) => {
    // Se o cliente excluído era o que estava selecionado na tela...
    if (selectedCompany && selectedCompany.id === deletedCompanyId) {
      setSelectedCompany(null); // Limpa o cliente selecionado
      setActiveView('general'); // Retorna para o dashboard geral
    }
    // Ativa o gatilho para que a Sidebar recarregue a lista de clientes
    setRefreshClients(prev => !prev); 
  };

  // Função para renderizar a página correta com base no estado 'activeView'
  const renderActiveView = () => {
    if (!selectedCompany) {
      return (
        <div className="welcome-message">
          <h2>Bem-vindo ao RADAR OPTMUS</h2>
          <p>Selecione um cliente na barra lateral para começar ou cadastre um novo cliente clicando no botão `+`.</p>
        </div>
      );
    }

    switch (activeView) {
      case 'general':
        // CORREÇÃO APLICADA AQUI: Passando a prop onViewChange
        return <GeneralDashboard company={selectedCompany} onViewChange={setActiveView} />;
      case 'alerts':
        return <AlertsDashboard company={selectedCompany} />;
      case 'market':
        return <MarketAnalysisPage company={selectedCompany} />;
      case 'recommendations':
        return <RecommendationsPage company={selectedCompany} />;
      case 'billing':
        return <MonthlyBillingPage company={selectedCompany} />;
      case 'financials':
        return <FinancialDashboardPage company={selectedCompany} />;
      case 'debts':
        return <DebtAnalysisPage company={selectedCompany} />;
      case 'contracts':
        return <ContractsPage company={selectedCompany} />;
      default:
        return <GeneralDashboard company={selectedCompany} onViewChange={setActiveView} />;
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
        onCompanyDelete={handleCompanyDeleted} 
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

      {/* O Modal é renderizado aqui, mas só é visível se 'modalContent' não for nulo */}
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