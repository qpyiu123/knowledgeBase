import { MantineProvider, createTheme, type MantineColorsTuple } from '@mantine/core';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import '@mantine/core/styles.css';
import './styles.css';

// 与参考设计一致的墨绿主色
const brand: MantineColorsTuple = [
  '#e6f6f2',
  '#ccece5',
  '#a3dcd1',
  '#78cbbd',
  '#57bcac',
  '#43b0a0',
  '#35a996',
  '#229c85',
  '#0f8b74',
  '#087f6b',
];

const theme = createTheme({
  primaryColor: 'brand',
  colors: { brand },
  fontFamily:
    '"Segoe UI","Microsoft YaHei",system-ui,-apple-system,sans-serif',
  fontFamilyMonospace: "Consolas,'Cascadia Code','JetBrains Mono',monospace",
  defaultRadius: 'md',
  headings: { fontWeight: '650' },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider theme={theme} defaultColorScheme="auto">
      <App />
    </MantineProvider>
  </StrictMode>,
);
