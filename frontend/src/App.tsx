import React from "react";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import DashboardLayout from "./components/DashboardLayout";

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      paper: "#121212",
    }
  },
  components: {
    MuiDialog:{
      styleOverrides: {
        paper: {
          backgroundImage: "none"
        }
      },
    }
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <WebSocketProvider>
        <DashboardLayout />
      </WebSocketProvider>
    </ThemeProvider>
  );
};

export default App;
