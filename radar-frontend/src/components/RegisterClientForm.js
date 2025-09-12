import React, { useState } from 'react';
import './RegisterClientForm.css';

const RegisterClientForm = ({ onSuccess, onCancel }) => {
  const [alias, setAlias] = useState('');
  const [cnpj, setCnpj] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/clientes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alias, cnpj })
      });
      const data = await response.json();
      if (response.ok) {
        alert('Cliente cadastrado com sucesso!');
        onSuccess();
      } else {
        alert(`Erro: ${data.error || data.message}`);
      }
    } catch (err) {
      alert('Erro de conexão ao cadastrar cliente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <h3>Cadastrar Novo Cliente</h3>
      <div className="form-group">
        <label htmlFor="alias">Nome de Identificação (Apelido)</label>
        <input id="alias" value={alias} onChange={(e) => setAlias(e.target.value)} required />
      </div>
      <div className="form-group">
        <label htmlFor="cnpj">CNPJ</label>
        <input id="cnpj" value={cnpj} onChange={(e) => setCnpj(e.target.value)} required />
      </div>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={isSubmitting}>Cancelar</button>
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Salvando...' : 'Salvar Cliente'}
        </button>
      </div>
    </form>
  );
};

export default RegisterClientForm;