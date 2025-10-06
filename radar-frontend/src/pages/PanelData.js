// src/pages/PanelData.js

import * as React from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Skeleton from '@mui/material/Skeleton';
import ChartUserCorp from "../components/ChartUserCorp";
import CustomizedTreeView from '../components/CustomizedTreeView';
import CustomizedDataGrid from '../components/CustomizedDataGrid';
import PageViewsBarChart from '../components/PageViewsBarChart';
import SessionsChart from "../components/SessionChat";
import StatCard from '../components/StatCard';

const data = [
  {
    title: 'Users',
    value: '14k',
    interval: 'Last 30 days',
    trend: 'up',
    data: [
      200, 24, 220, 260, 240, 380, 100, 240, 280, 240, 300, 340, 320, 360, 340, 380,
      360, 400, 380, 420, 400, 640, 340, 460, 440, 480, 460, 600, 880, 920,
    ],
  },
  {
    title: 'Conversions',
    value: '325',
    interval: 'Last 30 days',
    trend: 'down',
    data: [
      1640, 1250, 970, 1130, 1050, 900, 720, 1080, 900, 450, 920, 820, 840, 600, 820,
      780, 800, 760, 380, 740, 660, 620, 840, 500, 520, 480, 400, 360, 300, 220,
    ],
  },
  {
    title: 'Event count',
    value: '200k',
    interval: 'Last 30 days',
    trend: 'neutral',
    data: [
      500, 400, 510, 530, 520, 600, 530, 520, 510, 730, 520, 510, 530, 620, 510, 530,
      520, 410, 530, 520, 610, 530, 520, 610, 530, 420, 510, 430, 520, 510,
    ],
  },
];

export default function PanelData() {
  const [loading, setLoading] = React.useState(true);

  // 🔍 Log de depuração
  console.log('%cPainel de Dados carregado', 'color: #00bcd4; font-weight: bold;');

  React.useEffect(() => {
    console.log('%cExecutando useEffect do PanelData', 'color: #9c27b0; font-weight: bold;');
    const timer = setTimeout(() => {
      setLoading(false);
      console.log('%cDados carregados no PanelData!', 'color: #4caf50; font-weight: bold;');
    }, 2000);
    return () => {
      clearTimeout(timer);
      console.log('%cPanelData desmontado', 'color: #f44336; font-weight: bold;');
    };
  }, []);

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}></Typography>
      <Grid container spacing={2} columns={12} sx={{ mb: (theme) => theme.spacing(2) }}>
        {data.map((card, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, lg: 3 }}>
            {loading ? (
              <Skeleton
                variant="rectangular"
                animation="wave"
                width="100%"
                height={120}
                sx={{ borderRadius: 2 }}
              />
            ) : (
              <StatCard {...card} />
            )}
          </Grid>
        ))}

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          {loading ? (
            <Skeleton
              variant="rectangular"
              animation="wave"
              width="100%"
              height={120}
              sx={{ borderRadius: 2 }}
            />
          ) : (
            <div></div>
          )}
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          {loading ? (
            <Skeleton
              variant="rectangular"
              animation="wave"
              width="100%"
              height={300}
              sx={{ borderRadius: 2 }}
            />
          ) : (
            <SessionsChart />
          )}
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          {loading ? (
            <Skeleton
              variant="rectangular"
              animation="wave"
              width="100%"
              height={300}
              sx={{ borderRadius: 2 }}
            />
          ) : (
            <PageViewsBarChart />
          )}
        </Grid>
      </Grid>

      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Details
      </Typography>

      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12, lg: 9 }}>
          {loading ? (
            <Skeleton
              variant="rectangular"
              animation="wave"
              width="100%"
              height={400}
              sx={{ borderRadius: 2 }}
            />
          ) : (
            <CustomizedDataGrid />
          )}
        </Grid>

        <Grid size={{ xs: 12, lg: 3 }}>
          {loading ? (
            <Stack gap={2} direction={{ xs: 'column', sm: 'row', lg: 'column' }}>
              <Skeleton
                variant="rectangular"
                animation="wave"
                width="100%"
                height={200}
                sx={{ borderRadius: 2 }}
              />
              <Skeleton
                variant="rectangular"
                animation="wave"
                width="100%"
                height={200}
                sx={{ borderRadius: 2 }}
              />
            </Stack>
          ) : (
            <Stack gap={2} direction={{ xs: 'column', sm: 'row', lg: 'column' }}>
              <CustomizedTreeView />
              <ChartUserCorp />
            </Stack>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
