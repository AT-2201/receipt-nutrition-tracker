export default function NutritionResult({ data }) {
  if (!data) return null;

  return (
    <div>
      <h2>Nutrition Summary</h2>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Item</th>
            <th>Calories</th>
            <th>Protein (g)</th>
            <th>Carbs (g)</th>
            <th>Fat (g)</th>
          </tr>
        </thead>
        <tbody>
          {data.nutrition.map((item, idx) => (
            <tr key={idx}>
              <td>{item.item_name}</td>
              <td>{item.calories}</td>
              <td>{item.protein}</td>
              <td>{item.carbs}</td>
              <td>{item.fat}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
