import React, { useState } from 'react';
// Reutilizaremos o mesmo CSS do formulário de registro para consistência
import './RegisterClientForm.css';

const FinancialDataForm = ({ company, onSuccess, onCancel }) => {
  const [revenue, setRevenue] = useState(company.annual_revenue || '');
  const [cashFlow, setCashFlow] = useState(company.monthly_cash_flow || '');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // Envia as duas atualizações para a API
      const revenuePromise = fetch(`http://127.0.0.1:5000/api/financeiro/faturamento/${company.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ annual_revenue: parseFloat(revenue) })
      });
      const cashFlowPromise = fetch(`http://127.0.0.1:5000/api/financeiro/fluxo-caixa/${company.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ monthly_cash_flow: parseFloat(cashFlow) })
      });

      // Espera ambas as requisições terminarem
      const [revenueRes, cashFlowRes] = await Promise.all([revenuePromise, cashFlowPromise]);

      if (revenueRes.ok && cashFlowRes.ok) {
        alert('Dados financeiros atualizados com sucesso!');
        onSuccess({ ...company, annual_revenue: revenue, monthly_cash_flow: cashFlow });
      } else {
        alert('Ocorreu um erro ao atualizar os dados.');
      }
    } catch (err) {
      alert('Erro de conexão ao atualizar dados financeiros.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <h3>Informar Dados Financeiros</h3>
      <p>Esses dados são essenciais para a Análise de Mercado e outras funcionalidades.</p>
      <div className="form-group">
        <label htmlFor="revenue">Faturamento Anual (ex: 1200000.00)</label>
        <input id="revenue" type="number" step="0.01" value={revenue} onChange={(e) => setRevenue(e.target.value)} required />
      </div>
      <div className="form-group">
        <label htmlFor="cashFlow">Fluxo de Caixa Mensal (Líquido)</label>
        <input id="cashFlow" type="number" step="0.01" value={cashFlow} onChange={(e) => setCashFlow(e.target.value)} required />
      </div>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={isSubmitting}>Cancelar</button>
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Salvando...' : 'Salvar Dados'}
        </button>
      </div>
    </form>
  );
};

export default FinancialDataForm;
