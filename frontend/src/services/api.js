const BASE_URL = "http://127.0.0.1:8000";

export async function uploadReceipt(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/receipts/upload`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}

export async function getNutrition(receiptId) {
  const res = await fetch(
    `${BASE_URL}/receipts/nutrition/${receiptId}`,
    { method: "POST" }
  );

  return res.json();
}
