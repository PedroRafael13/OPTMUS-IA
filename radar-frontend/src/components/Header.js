// radar-frontend/src/components/Header.js

import React from 'react';
import './Header.css';

function Header({ company }) {
  return (
    <header className="header">
      <div className="header-title">
        <h2>Dashboard Geral</h2>
        <span>{company ? company.internal_alias : 'Nenhum cliente selecionado'}</span>
      </div>
      <div className="header-actions">
        <button className="btn">Exportar</button>
        <button className="btn btn-primary">Atualizar</button>
      </div>
    </header>
  );
}

export default Header;