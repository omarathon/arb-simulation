import React from "react";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import DashboardLayout from "./components/DashboardLayout";

const App: React.FC = () => {
  return (
    <WebSocketProvider>
      <DashboardLayout />
    </WebSocketProvider>
  );
};

export default App;
