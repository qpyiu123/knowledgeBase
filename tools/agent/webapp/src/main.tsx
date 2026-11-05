import { MantineProvider, createTheme, type MantineColorsTuple } from '@mantine/core';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import '@mantine/core/styles.css';
import './styles.css';

const brand: MantineColorsTuple = [
  '#eff5ff',
  '#dbe8ff',
  '#b9d2ff',
  '#90b8fb',
  '#6495ee',
  '#4778da',
  '#3569ca',
  '#2859b6',
  '#204a98',
  '#193d7c',
];

const theme = createTheme({
  primaryColor: 'brand',
  primaryShade: { light: 7, dark: 7 },
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
