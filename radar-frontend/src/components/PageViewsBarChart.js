import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Chip from '@mui/material/Chip';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import { BarChart } from '@mui/x-charts/BarChart';
import { useTheme } from '@mui/material/styles';

export default function RoiBarChart() {
  const theme = useTheme();
  const colorPalette = [
    (theme.vars || theme).palette.success.dark,   // Retorno
    (theme.vars || theme).palette.error.light,   // Investimento
  ];

  return (
    <Card variant="outlined" sx={{ width: '100%' }}>
      <CardContent>
        <Typography component="h2" variant="subtitle2" gutterBottom>
          ROI por Campanha
        </Typography>
        <Stack sx={{ justifyContent: 'space-between' }}>
          <Stack
            direction="row"
            sx={{
              alignContent: { xs: 'center', sm: 'flex-start' },
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Typography variant="h4" component="p">
              R$ 120K
            </Typography>
            <Chip size="small" color="success" label="+15%" />
          </Stack>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Retorno sobre investimento dos últimos 6 meses
          </Typography>
        </Stack>
        <BarChart
          borderRadius={8}
          colors={colorPalette}
          xAxis={[
            {
              scaleType: 'band',
              categoryGapRatio: 0.5,
              data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
              height: 24,
            },
          ]}
          yAxis={[{ width: 60 }]}
          series={[
            {
              id: 'investimento',
              label: 'Investimento',
              data: [5000, 7000, 6000, 8000, 7500, 6500],
              stack: 'A',
            },
            {
              id: 'retorno',
              label: 'Retorno',
              data: [12000, 15000, 13000, 20000, 18000, 16000],
              stack: 'A',
            },
          ]}
          height={250}
          margin={{ left: 0, right: 0, top: 20, bottom: 0 }}
          grid={{ horizontal: true }}
        />
      </CardContent>
    </Card>
  );
}
