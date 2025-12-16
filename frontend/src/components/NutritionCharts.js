import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

export default function NutritionCharts({ data }) {
  if (!data || !data.nutrition || data.nutrition.length === 0) return null;

  // Aggregate macros
  const totals = data.nutrition.reduce(
    (acc, item) => {
      acc.protein += item.protein;
      acc.carbs += item.carbs;
      acc.fat += item.fat;
      return acc;
    },
    { protein: 0, carbs: 0, fat: 0 }
  );

  // Pie chart (macros)
  const pieData = {
    labels: ["Protein (g)", "Carbs (g)", "Fat (g)"],
    datasets: [
      {
        data: [
          totals.protein.toFixed(1),
          totals.carbs.toFixed(1),
          totals.fat.toFixed(1)
        ],
        backgroundColor: ["#4CAF50", "#2196F3", "#FF9800"]
      }
    ]
  };

  // Bar chart (calories per item)
  const barData = {
    labels: data.nutrition.map(i => i.item_name),
    datasets: [
      {
        label: "Calories",
        data: data.nutrition.map(i => i.calories),
        backgroundColor: "#673AB7"
      }
    ]
  };

  return (
    <div style={{ marginTop: "40px" }}>
      <h2>Macro Breakdown</h2>
      <Pie data={pieData} />

      <h2 style={{ marginTop: "40px" }}>Calories per Item</h2>
      <Bar data={barData} />
    </div>
  );
}
