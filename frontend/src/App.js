import { useEffect, useState } from "react";
import UploadReceipt from "./components/UploadReceipt";
import NutritionResult from "./components/NutritionResult";
import NutritionCharts from "./components/NutritionCharts";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <div className="app-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1 className="app-title">🥗 Receipt → Nutrition Tracker</h1>
        <button onClick={toggleTheme}>
          {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
        </button>
      </div>

      <div className="card">
        <UploadReceipt onResult={setResult} />
      </div>

      {result && (
        <>
          <div className="card">
            <NutritionResult data={result} />
          </div>

          <div className="card">
            <NutritionCharts data={result} />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
