import React, { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

// Inject CSS styles
const DashboardStyles = () => (
  <style>{`
    :root {
      --primary-color: #4f46e5;
      --primary-hover-color: #4338ca;
      --background-color: #f9fafb;
      --card-background: #ffffff;
      --text-primary: #1f2937;
      --text-secondary: #6b7280;
      --border-color: #e5e7eb;
      --font-family: 'Inter', sans-serif;
      --shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    body {
      font-family: var(--font-family);
      margin: 0;
      background: linear-gradient(135deg, #f0f4ff, #e6e9ff);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;   /* Vertical center */
  justify-content: center; /* Horizontal center */
  padding: 2rem;
}

.card {
  background: var(--card-background);
  padding: 3rem;
  border-radius: 1.25rem;
  box-shadow: var(--shadow);
  width: 100%;
  max-width: 900px;   /* keep card size fixed and centered */
  margin: auto;
}

    .card h1 {
      text-align: center;
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 2rem;
      background: linear-gradient(135deg, var(--primary-color), #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
    }

    @media (max-width: 768px) {
      .form-grid {
        grid-template-columns: 1fr;
      }
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .form-input {
      width: 80%;
      padding: 0.75rem 1rem;
      border: 2px solid var(--border-color);
      border-radius: 0.5rem;
      font-size: 1rem;
      background: #fafafa;
      transition: 0.3s;
    }

    .form-input:focus {
      border-color: var(--primary-color);
      background: #fff;
      outline: none;
    }

    .button {
      width: 100%;
      padding: 1rem;
      margin-top: 2rem;
      border-radius: 0.75rem;
      background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
      color: white;
      font-weight: 600;
      font-size: 1rem;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
      transition: 0.3s;
    }

    .button:hover {
      transform: translateY(-2px);
    }

    .result-card {
      background: var(--card-background);
      padding: 2.5rem;
      border-radius: 1rem;
      box-shadow: var(--shadow);
      margin-top: 2rem;
      text-align: center;
    }

    .result-card h2 {
      color: var(--primary-color);
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }

    .result-card ul {
      text-align: left;
      margin: 1rem auto;
      max-width: 500px;
    }

    .chart-container {
      height: 300px;
      margin: 2rem auto;
    }
  `}</style>
);

const App = () => {
  const [studentData, setStudentData] = useState({
    student_id: "",
    age_at_enrollment: "",
    gender: 0,
    scholarship_holder: 0,
    curricular_units_1st_sem_enrolled: "",
    curricular_units_1st_sem_approved: "",
    curricular_units_1st_sem_grade: "",
    curricular_units_2nd_sem_enrolled: "",
    curricular_units_2nd_sem_approved: "",
    curricular_units_2nd_sem_grade: "",
    debtor: 0,
    tuition_fees_up_to_date: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setStudentData({ ...studentData, [name]: value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        ...studentData,
        age_at_enrollment: Number(studentData.age_at_enrollment),
        gender: Number(studentData.gender),
        scholarship_holder: Number(studentData.scholarship_holder),
        curricular_units_1st_sem_enrolled: Number(studentData.curricular_units_1st_sem_enrolled),
        curricular_units_1st_sem_approved: Number(studentData.curricular_units_1st_sem_approved),
        curricular_units_1st_sem_grade: Number(studentData.curricular_units_1st_sem_grade),
        curricular_units_2nd_sem_enrolled: Number(studentData.curricular_units_2nd_sem_enrolled),
        curricular_units_2nd_sem_approved: Number(studentData.curricular_units_2nd_sem_approved),
        curricular_units_2nd_sem_grade: Number(studentData.curricular_units_2nd_sem_grade),
        debtor: Number(studentData.debtor),
        tuition_fees_up_to_date: Number(studentData.tuition_fees_up_to_date),
      };

      const response = await fetch("http://localhost:8000/predict-and-recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json();
        setError(errData.detail || "Unknown error");
      } else {
        const data = await response.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
      setError("Network error. Is the backend running on port 8000?");
    }

    setLoading(false);
  };

  return (
    <>
      <DashboardStyles />
      <div className="container">
        <div className="card">
          <h1>Student Risk Prediction</h1>

          {/* Form */}
          {!result && (
            <>
              <div className="form-grid">
                {[
                  { label: "Student ID", name: "student_id", type: "text" },
                  { label: "Age at enrollment", name: "age_at_enrollment", type: "number" },
                  { label: "Gender (0=Male, 1=Female)", name: "gender", type: "number" },
                  { label: "Scholarship holder (0=No, 1=Yes)", name: "scholarship_holder", type: "number" },
                  { label: "Curricular units 1st sem enrolled", name: "curricular_units_1st_sem_enrolled", type: "number" },
                  { label: "Curricular units 1st sem approved", name: "curricular_units_1st_sem_approved", type: "number" },
                  { label: "Curricular units 1st sem grade", name: "curricular_units_1st_sem_grade", type: "number", step: "0.1" },
                  { label: "Curricular units 2nd sem enrolled", name: "curricular_units_2nd_sem_enrolled", type: "number" },
                  { label: "Curricular units 2nd sem approved", name: "curricular_units_2nd_sem_approved", type: "number" },
                  { label: "Curricular units 2nd sem grade", name: "curricular_units_2nd_sem_grade", type: "number", step: "0.1" },
                  { label: "Debtor (0=No, 1=Yes)", name: "debtor", type: "number" },
                  { label: "Tuition fees up to date (0=No, 1=Yes)", name: "tuition_fees_up_to_date", type: "number" },
                ].map((field, i) => (
                  <div key={i} className="form-group">
                    <label>{field.label}</label>
                    <input
                      type={field.type}
                      step={field.step || "1"}
                      name={field.name}
                      className="form-input"
                      value={studentData[field.name]}
                      onChange={handleChange}
                    />
                  </div>
                ))}
              </div>

              <button className="button" onClick={handleSubmit} disabled={loading}>
                {loading ? "Predicting..." : "Predict Risk"}
              </button>

              {error && <div className="result error">{JSON.stringify(error)}</div>}
            </>
          )}

          {/* Output */}
          {result && !error && (
            <div className="result-card">
              <h2>Prediction Result</h2>
              <p><b>Risk Score:</b> {result.Risk_Score}</p>
              <p><b>Prediction:</b> {result.Prediction_Label}</p>

              {/* Graph */}
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: "Risk Score", value: result.Risk_Score },
                        { name: "Remaining", value: 100 - result.Risk_Score }
                      ]}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={100}
                      label
                    >
                      <Cell fill="#ef4444" />
                      <Cell fill="#22c55e" />
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <h3>Recommendations:</h3>
              <ul>
                {result.Recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>

              <button className="button" onClick={() => setResult(null)}>
                Back to Form
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default App;
