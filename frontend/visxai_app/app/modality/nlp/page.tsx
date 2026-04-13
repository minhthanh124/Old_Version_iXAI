'use client';

import React, { useState } from 'react';
import { ModelUploader, Dataset_Uploader, LabelUploader, TokenizerUploader } from "@/components/FileUploadPanel";
import {TaskPanel} from "@/components/TaskSelectionPanel";
import {HomeTabPanel} from "@/components/HomeTabPanel";
import ExplanationResult from '@/components/ExplanationPanel'
import {ShapGuideline} from "@/components/ShapGuideline";

const NLPPage = () => {
  const [showResult, setShowResult] = useState(false);
  const [trigger, setTrigger] = useState<number>(0)
  const [isSelectDisabled, setIsSelectDisabled] = useState(true);
  const [selectedMethod, setSelectedMethod] = useState('SHAP');
  localStorage.setItem("SessionMethod", selectedMethod)

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
            modality_name="Natural Language Processing"
            task_name={['Text Classification', 'Question Answering']}
            onTaskSelect={() => {}}
            description={{
              'Text Classification': "AI reads your text and figures out what it's about - like whether a message is positive or negative, or what topic it's related to. Then, it highlights the words that influenced its decision.",
              'Question Answering': 'AI reads your text and shows which parts of the text helped it choose that answer.'
            }}
        />

        {/* Main Panel */}
        <div className="flex flex-col w-3/4 space-y-6">
            <div className="bg-gray-50 p-6 rounded-lg shadow-md">
              <div className="grid grid-cols-2 gap-6">
              <div>
            <Dataset_Uploader
              title="Upload Your Text"
              label="Drop your .txt file here or click to choose."
              accept=".txt"
              description="For Question & Answering Text, specify between question part and answer part by [SEP]"/>

            </div>
            <div>
            <ModelUploader
              title="Upload Your Trained Model"
              label="Use a .pytorch model file."
              accept=".pth"
              description=""/>
            </div>
            <div>
            <LabelUploader
              title="Upload Labels"
              label="Add .txt or .json label files."
              accept=".txt,.json"
              description="The format of label file sames as: {key_1: value_1, key_2: value_2}"/>
            </div>
            <div>
            <TokenizerUploader
              title="Upload Tokenizer"
              label="Use .txt or .json tokenizer files."
              accept=".txt,.json"
              description="The tokenizer must be matched your uploaded model"/>
            </div>

            {/* Dropdowns */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 inline-block mr-2 ">Explanation Methods</h3>
              <span className="text-blue-500 text-2xl cursor-help inline-block mb-2" title="SHAP shows how each part of your text affects the result">ℹ️</span>
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
            className="text-2xl bg-indigo-900 text-white px-6 py-3 rounded-lg hover:bg-indigo-800"
          >
            Start Explanation
          </button>

          <button
            onClick={handleGetExample}
            className="text-2xl bg-indigo-900 text-white px-6 py-3 rounded-lg hover:bg-indigo-800"
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

export default NLPPage;
