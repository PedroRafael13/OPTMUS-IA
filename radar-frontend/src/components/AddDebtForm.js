import React, { useState } from 'react';
// Reutilizaremos o CSS do formulário de registro para manter a consistência
import './RegisterClientForm.css';

const AddDebtForm = ({ company, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    debt_type: 'Bancária',
    creditor: '',
    balance: '',
    details: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/debts/${company.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, balance: parseFloat(formData.balance) })
      });
      if (response.ok) {
        alert('Dívida adicionada com sucesso!');
        onSuccess();
      } else {
        const data = await response.json();
        alert(`Erro: ${data.error || 'Falha ao adicionar dívida.'}`);
      }
    } catch (err) {
      alert('Erro de conexão ao adicionar dívida.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <h3>Adicionar Dívida Manualmente</h3>
      <div className="form-group">
        <label htmlFor="debt_type">Tipo da Dívida</label>
        <select id="debt_type" name="debt_type" value={formData.debt_type} onChange={handleInputChange}>
          <option value="Bancária">Bancária</option>
          <option value="Fornecedor">Fornecedor</option>
          <option value="Protesto">Protesto</option>
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="creditor">Nome do Credor</label>
        <input id="creditor" name="creditor" value={formData.creditor} onChange={handleInputChange} required />
      </div>
      <div className="form-group">
        <label htmlFor="balance">Valor (R$)</label>
        <input id="balance" name="balance" type="number" step="0.01" value={formData.balance} onChange={handleInputChange} required />
      </div>
       <div className="form-group">
        <label htmlFor="details">Detalhes (Opcional)</label>
        <input id="details" name="details" value={formData.details} onChange={handleInputChange} />
      </div>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={isSubmitting}>Cancelar</button>
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Salvando...' : 'Salvar Dívida'}
        </button>
      </div>
    </form>
  );
};

export default AddDebtForm;
