// src/pages/GeneralDashboard.js

import React, { useState, useEffect } from 'react';
import KpiCard from '../components/KpiCard';
import RevenueChart from '../components/RevenueChart';

const GeneralDashboard = ({ company }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (company) {
      const fetchDashboardData = async () => {
        setIsLoading(true);
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/dashboard/general/${company.id}`);
          const data = await response.json();
          setDashboardData(data);
        } catch (error) {
          console.error("Erro ao buscar dados do dashboard:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchDashboardData();
    }
  }, [company]);

  if (isLoading) return <p>Carregando dashboard...</p>;
  if (!dashboardData) return <p>Não foi possível carregar os dados do dashboard.</p>;

  return (
    <>
      <div className="kpi-grid">
        <KpiCard title="Receita Mensal" value={`R$ ${(dashboardData.monthly_revenue / 1000).toFixed(1)}K`} subtitle={`${dashboardData.revenue_change_percent.toFixed(1)}% vs período anterior`} change={dashboardData.revenue_change_percent} />
        <KpiCard title="Contratos Ativos" value={dashboardData.active_contracts} subtitle={`Ticket médio: R$ ${(dashboardData.average_ticket / 1000).toFixed(1)}K`} />
        <KpiCard title="Market Share" value={`${(dashboardData.market_share || 0).toFixed(2)}%`} subtitle={dashboardData.market_rank} />
        <KpiCard title="Crescimento" value={`${dashboardData.revenue_change_percent.toFixed(1)}%`} subtitle="Últimos 30 dias" />
      </div>
      <RevenueChart data={dashboardData.revenue_evolution_data} />
    </>
  );
};

export default GeneralDashboard;