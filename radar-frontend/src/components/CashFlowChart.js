import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './RevenueChart.css'; // Podemos reutilizar o mesmo estilo

const CashFlowChart = ({ data }) => {
  return (
    <div className="chart-container">
      <h3>Projeção de Fluxo de Caixa (Próximos 6 meses)</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis yAxisId="left" tickFormatter={(value) => `R$ ${value/1000}K`} />
          <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => `R$ ${value/1000}K`} />
          <Tooltip formatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`} />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="Entradas" stroke="#28a745" strokeWidth={2} />
          <Line yAxisId="left" type="monotone" dataKey="Saídas" stroke="#dc3545" strokeWidth={2} />
          <Line yAxisId="right" type="monotone" dataKey="Saldo" stroke="#007bff" strokeWidth={3} activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CashFlowChart;