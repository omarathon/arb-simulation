import React from "react";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import OddsTable from "./components/OddsTable";

const App: React.FC = () => {
  return (
    <WebSocketProvider>
      <OddsTable />
    </WebSocketProvider>
  );
};

export default App;
