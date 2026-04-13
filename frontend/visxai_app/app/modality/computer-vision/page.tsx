'use client';

import React, { useState } from 'react';
import { ModelUploader, Dataset_Uploader, LabelUploader } from "@/components/FileUploadPanel";
import {TaskPanel} from "@/components/TaskSelectionPanel";
import {HomeTabPanel} from "@/components/HomeTabPanel";
import ExplanationResult from '@/components/ExplanationPanel'
import { useLayerStore, useObjectStore } from '@/shared/store';
import {GradCamGuideline} from "@/components/GradcamGuideline";

const ComputerVisionPage = () => {
  const [showResult, setShowResult] = useState(false);
  const [trigger, setTrigger] = useState<number>(0)
  const [isSelectDisabled, setIsSelectDisabled] = useState(true);
  const [selectedMethod, setSelectedMethod] = useState('GradCAM');
  const [selectedLayer, setSelectedLayer] = useState('');
  const [selectedObject, setSelectedObject] = useState('');
  localStorage.setItem("SessionMethod", selectedMethod)
  const layers = useLayerStore((state) => state.layers);
  const objects = useObjectStore((state) => state.objects);

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

  const handleLayersChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const layer = e.target.value;
      setSelectedLayer(layer);
      localStorage.setItem("SessionSelectedLayer", layer)
  };

  const handleObjectsChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const object = e.target.value;
      setSelectedObject(object);
      localStorage.setItem("SessionSelectedObject", object)
  };

  const handleGetExample = () => {

  };

return (
<div className="min-h-screen bg-white px-6 py-10">
  <HomeTabPanel />
  <div className="flex">
    {/* Sidebar on the left */}
    <TaskPanel
      modality_name="Computer Vision"
      task_name={['Image Classification', 'Image Segmentation']}
      onTaskSelect={() => {}}
      description={{
        'Image Classification': 'AI looks at your image and tells you what it sees - like a cat, a car, or a tree. It also highlights the parts of the image that helped it make that decision.',
        'Image Segmentation': 'AI breaks the image into parts and shows exactly where each object is - like outlining the cat, the road, or the tree in the picture.'
      }}
    />

    {/* Right main column */}
    <div className="flex flex-col w-3/4 space-y-6">
      {/* Form panel */}
      <div className="bg-gray-50 p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-2 gap-6">
          {/* File uploaders */}
          <div>
            <Dataset_Uploader
              title="Upload Images"
              label="Upload png, jpeg, or jpg files"
              accept=".png,.jpg,.jpeg"
              description=""
            />
          </div>

          <div>
            <ModelUploader
              title="Upload Your Trained Model"
              label="Use a .pytorch model file with CNN architecture."
              accept=".pth"
              description="The model should include both the architecture and weights. Models with only weights (without architecture) are not supported."
            />
          </div>

          <div>
            <LabelUploader
              title="Upload Labels"
              label="Add .xlsx or .csv label files."
              accept=".xlsx, .csv"
              description="For xlsx, csv label files, it should contain Index column (define class id) and Name column (define class name)"            
            />
          </div>

          {/* Dropdowns */}
          <div>
            <h3 className="text-2xl font-semibold text-gray-900 inline-block mr-2">Explanation Methods</h3>
            <span className="text-blue-500 text-2xl cursor-help inline-block mb-2" title="GradCAM shows which regions in an image that the model looked at the most to come to final prediction">ℹ️</span>
            <p className="text-xl text-sm text-gray-500 mb-2">Select which method to use for the explanation.</p>
            <select
              value={selectedMethod}
              onChange={handleMethodChange}
              className="block w-full mt-2 border rounded px-3 py-2"
            >
              <option value="GradCAM">GradCAM</option>
            </select>
          </div>

          <div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-1">Layers</h3>
            <p className="text-xl text-gray-500">Select which Conv layer to display the explanation</p>
            <select
              value={selectedLayer}
              onChange={handleLayersChange}
              className={`block w-full mt-2 border rounded px-3 py-2 ${
                isSelectDisabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''
              }`}
              disabled={isSelectDisabled}
            >
                {layers.map((layer) => (
                  <option key={layer} value={layer}>{layer}</option>
                ))}
            </select>
          </div>

          <div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-1">Objects</h3>
            <p className="text-xl text-gray-500">Select which object to display the explanation</p>
            <select
              value={selectedObject}
              onChange={handleObjectsChange}
              className={`block w-full mt-2 border rounded px-3 py-2 ${
                isSelectDisabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''
              }`}
              disabled={isSelectDisabled}
            >
              {objects.map((object) => (
                <option key={object} value={object}>{object}</option>
              ))}
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
  {showResult && <GradCamGuideline />}
</div>
);
};

export default ComputerVisionPage;