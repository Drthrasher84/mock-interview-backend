import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const questions = [
  "Can you walk me through the claims process?",
  "Describe a time when you had to handle a difficult customer. How did you manage the situation, and what was the outcome?",
  "Can you provide an example of a situation where you had to multitask under pressure? How did you prioritize your tasks and ensure everything was completed?",
  "Tell me about a time when you identified a problem in your work environment. What steps did you take to resolve it, and what was the result?"
];

export default function MockInterview() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [response, setResponse] = useState("");
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const analyzeResponseWithAI = async (answer) => {
    setLoading(true);
    try {
      const res = await fetch("https://mock-interview-backend-1.onrender.com/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: questions[currentQuestion], answer }),
      });
      const data = await res.json();
      setFeedback(data.feedback || "No feedback received.");

      // Save response and feedback to history
      setHistory((prev) => [...prev, { question: questions[currentQuestion], answer, feedback: data.feedback }]);
    } catch (error) {
      setFeedback("Error analyzing response. Please try again.");
    }
    setLoading(false);
  };

  const handleNextQuestion = async () => {
    if (!response.trim()) return;
    await analyzeResponseWithAI(response);
    
    setTimeout(() => {
      setCurrentQuestion((prev) => (prev + 1) % questions.length);
      setResponse("");
      setFeedback("");
    }, 5000);
  };

  return (
    <div className="flex flex-col items-center p-6">
      <Card className="w-full max-w-2xl p-4">
        <CardContent>
          <h2 className="text-xl font-bold">Mock Interview</h2>
          <p className="mt-4 text-lg font-semibold">{questions[currentQuestion]}</p>
          <Input
            className="mt-4"
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Type your answer here..."
          />
          <Button className="mt-4" onClick={handleNextQuestion} disabled={!response.trim() || loading}>
            {loading ? "Analyzing..." : "Submit Answer"}
          </Button>
          {feedback && (
            <div className="mt-4 p-3 border border-green-500 bg-green-100 rounded">
              <p className="text-green-700">{feedback}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Display Previous Responses */}
      <div className="w-full max-w-2xl mt-6">
        <h3 className="text-lg font-bold">Previous Responses</h3>
        {history.length > 0 ? (
          <ul className="mt-2 border p-4 rounded bg-gray-100">
            {history.map((entry, index) => (
              <li key={index} className="mb-2 border-b pb-2">
                <p className="font-semibold">Q: {entry.question}</p>
                <p className="italic">A: {entry.answer}</p>
                <p className="text-green-700">Feedback: {entry.feedback}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-gray-500">No responses yet.</p>
        )}
      </div>
    </div>
  );
}
