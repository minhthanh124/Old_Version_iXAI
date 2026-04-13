'use client';

import React, { useState } from 'react';
import { ModelUploader, Dataset_Uploader } from "@/components/FileUploadPanel";
import {TaskPanel} from "@/components/TaskSelectionPanel";
import {HomeTabPanel} from "@/components/HomeTabPanel";
import ExplanationResult from '@/components/ExplanationPanel'
import ShapGuideline from '@/components/ShapGuideline'

import {
  SESSION_ID,
} from '@/shared/constant';

import {updateModalityLocalStorage} from '@/shared/module';

const TBLPage = () => {
  const [selectedMethod, setSelectedMethod] = useState('SHAP');
  const [showResult, setShowResult] = useState(false);
  const [trigger, setTrigger] = useState<number>(0)
  const [isSelectDisabled, setIsSelectDisabled] = useState(true);
  localStorage.setItem("SessionMethod", selectedMethod)
  updateModalityLocalStorage(SESSION_ID, "Tabular Processing", "Tabular Classification");

  const handleStartExplanation = () => {
    setShowResult(false)
    setTrigger((prev) => prev + 1)
    setShowResult(true)
    setIsSelectDisabled(false);
  };

  const handleMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const method = e.target.value;
    setSelectedMethod(method);
    localStorage.setItem("SessionMethod", method)
  };

  const handleGetExample = () => {

  };

  return (
    <div className="min-h-screen bg-white px-6 py-10">
        <HomeTabPanel/>
      <div className="flex">
        {/* Sidebar */}
        <TaskPanel
            modality_name="Tabular Processing"
            task_name={['Tabular Classification']}
            onTaskSelect={() => {}}
            description={{
              'Tabular Classification': "AI looks at data in a table (like age, income, or product info) and predicts a result - such as whether a customer will buy something. Then, it highlights which features were most important in making that prediction.",
            }}
        />
        {/* Main Panel */}
        <div className="flex flex-col w-3/4 space-y-6">
            <div className="bg-gray-50 p-6 rounded-lg shadow-md">
              <div className="grid grid-cols-2 gap-6">
            <div>
            <Dataset_Uploader
              title="Upload Your Table Data"
              label="Use .csv or .xlsx data files."
              accept=".csv, .xlsx"
              description="The table data must contain a column named 'Class', indicating the label name"/>
            </div>
            <div>
            <ModelUploader
              title="Upload Your Trained Model"
              label="Use .pytorch or .pkl models."
              accept=".pth, .pkl"
              description=""/>
            </div>
            <div>
            </div>

            {/* Dropdowns */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 inline-block mr-2">Explanation Methods</h3>
              <span className="text-blue-500 text-2xl cursor-help inline-block mb-2" title="SHAP shows how each feature's contribution to model's prediction">ℹ️</span>
              <p className="text-xl text-gray-500 mb-2">Select which method to use for the explanation.</p>
              <select
                value={selectedMethod}
                onChange={handleMethodChange}
                className="block w-full mt-2 border rounded px-3 py-2"
              >
                <option value="SHAP">SHAP</option>
              </select>
            </div>
          </div>

        <div className="mt-8 flex justify-end space-x-4">
          <button
            onClick={handleStartExplanation}
            className="bg-indigo-900 text-2xl text-white px-6 py-3 rounded-lg hover:bg-indigo-800"
          >
            Start Explanation
          </button>

          <button
            onClick={handleGetExample}
            className="bg-indigo-900 text-2xl text-white px-6 py-3 rounded-lg hover:bg-indigo-800"
            title="See an example without uploading"
          >
            Use Example
          </button>
        </div>

        </div>
        {/* Result */}
        {showResult && (
        <div className="bg-gray-50 p-10 rounded-lg shadow-md">
          <ExplanationResult key={trigger} requestId={trigger} />
        </div>
        )}
      </div>
    </div>
    {showResult && <ShapGuideline />}
  </div>
  );
};

export default TBLPage;
