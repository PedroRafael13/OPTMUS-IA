import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import { SparkLineChart } from '@mui/x-charts/SparkLineChart';

// Esta função agora simula a variação de lucro diário.
function getDaysInMonth(month, year) {
  const date = new Date(year, month, 0);
  const monthName = date.toLocaleDateString('en-US', {
    month: 'short',
  });
  const daysInMonth = date.getDate();
  const days = [];
  let i = 1;
  while (days.length < daysInMonth) {
    days.push(`${monthName} ${i}`);
    i += 1;
  }
  return days;
}

// Adaptação: O gráfico de barra agora representa o ROI diário
function renderSparklineCell(params) {
  const data = getDaysInMonth(4, 2024);
  const { value, colDef } = params;

  if (!value || value.length === 0) {
    return null;
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
      <SparkLineChart
        data={value}
        width={colDef.computedWidth || 100}
        height={32}
        plotType="bar"
        showHighlight
        showTooltip
        color="hsl(210, 98%, 42%)"
        xAxis={{
          scaleType: 'band',
          data,
        }}
      />
    </div>
  );
}

// A função de status é mantida, pois o status de uma campanha também é relevante.
function renderStatus(status) {
  const colors = {
    Ativa: 'success',
    Pausada: 'default',
  };

  return <Chip label={status} color={colors[status]} size="small" />;
}

// O avatar pode ser adaptado para exibir o tipo de campanha, se necessário.
export function renderAvatar(params) {
  if (params.value == null) {
    return '';
  }

  return (
    <Avatar
      sx={{
        backgroundColor: params.value.color,
        width: '24px',
        height: '24px',
        fontSize: '0.85rem',
      }}
    >
      {params.value.name.toUpperCase().substring(0, 1)}
    </Avatar>
  );
}

export const columns = [
  { field: 'campaignName', headerName: 'Nome da Campanha', flex: 1.5, minWidth: 200 },
  {
    field: 'status',
    headerName: 'Status',
    flex: 0.5,
    minWidth: 80,
    renderCell: (params) => renderStatus(params.value),
  },
  {
    field: 'leads',
    headerName: 'Leads',
    headerAlign: 'right',
    align: 'right',
    flex: 1,
    minWidth: 80,
  },
  {
    field: 'conversions',
    headerName: 'Conversões',
    headerAlign: 'right',
    align: 'right',
    flex: 1,
    minWidth: 100,
  },
  {
    field: 'cost',
    headerName: 'Custo',
    headerAlign: 'right',
    align: 'right',
    flex: 1,
    minWidth: 120,
    // Adaptação: Formatação para moeda, se necessário.
    valueFormatter: (value) => `$${value}`,
  },
  {
    field: 'revenue',
    headerName: 'Receita',
    headerAlign: 'right',
    align: 'right',
    flex: 1,
    minWidth: 100,
    // Adaptação: Formatação para moeda.
    valueFormatter: (value) => `$${value}`,
  },
  {
    field: 'roi',
    headerName: 'ROI Diário',
    flex: 1,
    minWidth: 150,
    renderCell: renderSparklineCell,
  },
];

export const rows = [
  {
    id: 1,
    campaignName: 'Anúncios no Google',
    status: 'Ativa',
    leads: 212423,
    conversions: 8345,
    cost: 50000,
    revenue: 150000,
    roi: [
      1.5, 1.6, 1.8, 2.0, 2.1, 2.3, 2.5, 2.6, 2.8, 3.0,
      3.1, 3.3, 3.5, 3.6, 3.8, 4.0, 4.1, 4.3, 4.5, 4.6,
      4.8, 5.0, 5.1, 5.3, 5.5, 5.6, 5.8, 6.0, 6.1, 6.3,
    ],
  },
  {
    id: 2,
    campaignName: 'E-mail Marketing',
    status: 'Ativa',
    leads: 172240,
    conversions: 5653,
    cost: 15000,
    revenue: 45000,
    roi: [
      1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.1, 2.3, 2.5, 2.6,
      2.8, 3.0, 3.1, 3.3, 3.5, 3.6, 3.8, 4.0, 4.1, 4.3,
      4.5, 4.6, 4.8, 5.0, 5.1, 5.3, 5.5, 5.6, 5.8, 6.0,
    ],
  },
  {
    id: 3,
    campaignName: 'Anúncios no Facebook',
    status: 'Pausada',
    leads: 58240,
    conversions: 3455,
    cost: 25000,
    revenue: 75000,
    roi: [
      2.5, 2.6, 2.8, 3.0, 3.1, 3.3, 3.5, 3.6, 3.8, 4.0,
      4.1, 4.3, 4.5, 4.6, 4.8, 5.0, 5.1, 5.3, 5.5, 5.6,
      5.8, 6.0, 6.1, 6.3, 6.5, 6.6, 6.8, 7.0, 7.1, 7.3,
    ],
  },
  // Dados de exemplo adaptados para outras campanhas
  {
    id: 4,
    campaignName: 'Marketing de Conteúdo',
    status: 'Ativa',
    leads: 96240,
    conversions: 112543,
    cost: 30000,
    revenue: 100000,
    roi: [
      2.0, 2.1, 2.3, 2.5, 2.6, 2.8, 3.0, 3.1, 3.3, 3.5,
      3.6, 3.8, 4.0, 4.1, 4.3, 4.5, 4.6, 4.8, 5.0, 5.1,
      5.3, 5.5, 5.6, 5.8, 6.0, 6.1, 6.3, 6.5, 6.6, 6.8,
    ],
  },
  {
    id: 5,
    campaignName: 'Anúncios no Instagram',
    status: 'Pausada',
    leads: 142240,
    conversions: 3653,
    cost: 40000,
    revenue: 120000,
    roi: [
      1.8, 2.0, 2.1, 2.3, 2.5, 2.6, 2.8, 3.0, 3.1, 3.3,
      3.5, 3.6, 3.8, 4.0, 4.1, 4.3, 4.5, 4.6, 4.8, 5.0,
      5.1, 5.3, 5.5, 5.6, 5.8, 6.0, 6.1, 6.3, 6.5, 6.6,
    ],
  },
  // Remova os dados de 6 a 35 ou adapte-os de forma similar, preenchendo as novas colunas
];