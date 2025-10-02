// src/components/GenerateRecsForm.js
import React, { useState } from 'react';
import './RegisterClientForm.css'; // Reutilizando estilos

const GenerateRecsForm = ({ onSubmit, onCancel, isGenerating }) => {
  const [focusArea, setFocusArea] = useState('Marketing');
  const [objective, setObjective] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ focus_area: focusArea, objective });
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <h3>Gerar Novas Recomendações</h3>
      <p>Forneça um contexto para que a IA gere sugestões mais precisas.</p>
      
      <div className="form-group">
        <label htmlFor="focusArea">Área de Foco Principal</label>
        <select id="focusArea" value={focusArea} onChange={(e) => setFocusArea(e.target.value)}>
          <option value="Marketing">Marketing e Vendas</option>
          <option value="Financeiro">Financeiro</option>
          <option value="Comercial">Comercial e Operacional</option>
          <option value="Expansão">Expansão de Mercado</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="objective">Objetivo Específico</label>
        <textarea 
            id="objective" 
            rows="3"
            value={objective} 
            onChange={(e) => setObjective(e.target.value)} 
            placeholder="Ex: Aumentar a receita em 15% no próximo semestre, reduzir a inadimplência, capturar clientes do concorrente X, etc."
            required 
        />
      </div>

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={isGenerating}>Cancelar</button>
        <button type="submit" className="btn btn-primary" disabled={isGenerating}>
          {isGenerating ? 'Gerando...' : 'Gerar'}
        </button>
      </div>
    </form>
  );
};

export default GenerateRecsForm;