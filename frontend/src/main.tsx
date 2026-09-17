import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./i18n";
import "./index.css";
import { CurrencyProvider } from "./currency";
import { ThemeProvider } from "./theme";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <CurrencyProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </CurrencyProvider>
    </BrowserRouter>
  </StrictMode>,
);
