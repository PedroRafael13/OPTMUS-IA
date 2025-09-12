import React, { useState, useEffect, useCallback } from 'react';
import KpiCard from '../components/KpiCard';
import AlertCard from '../components/AlertCard';
import Modal from '../components/Modal'; // Importar Modal
import AddDebtForm from '../components/AddDebtForm'; // Importar novo formulário
import './DebtAnalysisPage.css';

const DebtAnalysisPage = ({ company }) => {
  const [debtData, setDebtData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0); // Para forçar a atualização

  const fetchDebtData = useCallback(async () => {
    if (!company) return;
    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/debts/${company.id}`);
      const data = await response.json();
      if (response.ok) {
        setDebtData(data);
      } else {
        throw new Error(data.error || 'Falha ao buscar dados.');
      }
    } catch (error) {
      console.error("Erro ao buscar dados de dívidas:", error);
      setDebtData(null); // Limpa dados em caso de erro para mostrar a mensagem correta
    } finally {
      setIsLoading(false);
    }
  }, [company]);

  useEffect(() => {
    fetchDebtData();
  }, [company, refreshKey, fetchDebtData]);

  const handleAddSuccess = () => {
    setIsModalOpen(false);
    setRefreshKey(prev => prev + 1); // Altera a chave para re-executar o fetch
  };

  if (isLoading) return <p>Carregando análise de dívidas...</p>;
  if (!debtData) return <p>Não foi possível carregar os dados. Verifique se o cliente possui dívidas ou adicione uma manualmente.</p>;

  const { totals, strategic_analysis, details } = debtData;

  return (
    <div className="debt-analysis-page">
      <div className="page-header">
        <h3>Análise de Dívidas</h3>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          Adicionar Dívida
        </button>
      </div>

      <div className="kpi-grid">
        <KpiCard title="Total de Dívidas" value={`R$ ${(totals.total_dividas / 1000).toFixed(1)}K`} />
        <KpiCard title="Dívidas Bancárias" value={`R$ ${(totals.total_bancario / 1000).toFixed(1)}K`} />
        <KpiCard title="Fornecedores" value={`R$ ${(totals.total_fornecedor / 1000).toFixed(1)}K`} />
        <KpiCard title="Protestos" value={`R$ ${(totals.total_protestos / 1000).toFixed(1)}K`} />
      </div>
      
      <div className="strategic-section">
        <h3>Análise Estratégica</h3>
        <div className="alerts-grid">
          {Object.entries(strategic_analysis).map(([key, value]) => (
              <AlertCard key={key} icon="💡" title={key.replace(/_/g, ' ')} description={value} />
          ))}
        </div>
      </div>

      <div className="details-section">
          <h3>Detalhamento das Dívidas</h3>
          {details && details.length > 0 ? (
            <ul>
              {details.map((debt, index) => (
                <li key={index}>
                  <strong>[{debt.debt_type}]</strong> {debt.creditor_name}: 
                  <span> R$ {debt.outstanding_balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                  {debt.details && <small> ({debt.details})</small>}
                </li>
              ))}
            </ul>
          ) : (
            <p>Nenhuma dívida registrada para este cliente.</p>
          )}
      </div>

      <Modal show={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <AddDebtForm
          company={company}
          onSuccess={handleAddSuccess}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </div>
  );
};

export default DebtAnalysisPage;
