// src/components/RevenueChart.js
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import './RevenueChart.css';

const RevenueChart = ({ data }) => {
  return (
    <div className="chart-container">
      <h3>Evolução da Receita</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(value) => `R$ ${value/1000}K`} />
          <Tooltip formatter={(value) => [`R$ ${value.toFixed(2)}`, "Receita"]} />
          <Line type="monotone" dataKey="Receita" stroke="#1e87f0" strokeWidth={3} activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RevenueChart;