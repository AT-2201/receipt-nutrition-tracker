import { useState } from "react";
import { uploadReceipt, getNutrition } from "../services/api";

export default function UploadReceipt({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
  try {
    if (!file) return alert("Select a receipt image");
    setLoading(true);

    const uploadRes = await uploadReceipt(file);
    console.log("UPLOAD RESPONSE:", uploadRes);

    const receiptId = uploadRes.receipt_id;

    const nutritionRes = await getNutrition(receiptId);
    console.log("NUTRITION RESPONSE:", nutritionRes);

    onResult(nutritionRes);
  } catch (err) {
    console.error("❌ Frontend error:", err);
    alert("Something failed. Check backend logs.");
  } finally {
    setLoading(false);
  }
};


  return (
    <div>
      <h2>Upload Grocery Receipt</h2>
      <p>Select a receipt image and get nutrition insights instantly.</p>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <br /><br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Analyze"}
      </button>
    </div>
  );
}
