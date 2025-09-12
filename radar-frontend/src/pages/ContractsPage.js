import React, { useState, useEffect } from 'react';
import './ContractsPage.css';

const ContractsPage = ({ company }) => {
  const [contracts, setContracts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    service: '',
    price: '',
    responsible: '',
    due_date: ''
  });

  const fetchContracts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/contratos/cliente/${company.id}`);
      const data = await response.json();
      setContracts(data);
    } catch (error) {
      console.error("Erro ao buscar contratos:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (company) {
      fetchContracts();
    }
  }, [company]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:5000/api/contratos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, company_id: company.id, price: parseFloat(formData.price) })
      });
      if (response.ok) {
        alert('Contrato adicionado com sucesso!');
        setShowForm(false);
        fetchContracts(); // Re-fetch contracts to update the list
      } else {
        alert('Falha ao adicionar contrato.');
      }
    } catch (error) {
      console.error("Erro ao adicionar contrato:", error);
    }
  };

  if (isLoading) return <p>Carregando contratos...</p>;

  return (
    <div className="contracts-page">
      <div className="contracts-header">
        <h3>Contratos Ativos ({contracts.length})</h3>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : 'Adicionar Contrato'}
        </button>
      </div>

      {showForm && (
        <div className="contract-form-container">
          <form onSubmit={handleSubmit}>
            <input name="service" value={formData.service} onChange={handleInputChange} placeholder="Descrição do Serviço" required />
            <input name="price" type="number" value={formData.price} onChange={handleInputChange} placeholder="Preço Mensal (ex: 4500.00)" required />
            <input name="responsible" value={formData.responsible} onChange={handleInputChange} placeholder="Responsável" />
            <input name="due_date" type="date" value={formData.due_date} onChange={handleInputChange} placeholder="Data de Vencimento" required />
            <button type="submit">Salvar Contrato</button>
          </form>
        </div>
      )}

      <div className="contracts-list">
        <table>
          <thead>
            <tr>
              <th>Serviço</th>
              <th>Preço Mensal</th>
              <th>Responsável</th>
              <th>Vencimento</th>
            </tr>
          </thead>
          <tbody>
            {contracts.map(contract => (
              <tr key={contract.contract_id}>
                <td>{contract.service_description}</td>
                <td>R$ {contract.monthly_price.toFixed(2)}</td>
                <td>{contract.responsible_person}</td>
                <td>{contract.due_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ContractsPage;