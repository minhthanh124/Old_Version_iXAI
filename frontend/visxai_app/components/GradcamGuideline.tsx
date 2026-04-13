"use client";
export const GradCamGuideline = () => (
  <div className="fixed bottom-2 left-5 bg-white p-3 rounded-lg shadow-md z-10 w-[550px]">
    <h3 className="text-2xl font-semibold text-gray-900 mb-2">Grad-CAM Guideline</h3>
    <p className="text-xl text-gray-600 mb-4">
      This GradCAM shows which regions of the image that AI model is looking at when making a decision. The colors help explain how important each part of the image matters to the model’s prediction.
      There are 4 color levels, each showing a different level of importance:
    </p>
    <ul className="list-none space-y-3">
      <li className="flex items-center">
        <span className="w-14 h-8 bg-red-600 mr-2"></span>
        <span className="text-xl text-gray-700">Highest attention - The model strongly focuses on this area to make its prediction.</span>
      </li>
      <li className="flex items-center">
        <span className="w-14 h-8 bg-yellow-400 mr-2"></span>
        <span className="text-xl text-gray-700">High attention - This area is important and helps guide the model’s decision.</span>
      </li>
      <li className="flex items-center">
        <span className="w-13 h-8 bg-green-400 mr-2"></span>
        <span className="text-xl text-gray-700">Moderate attention - This area has some influence, but not very strong.</span>
      </li>
      <li className="flex items-center">
        <span className="w-18 h-8 bg-blue-400 mr-2"></span>
        <span className="text-xl text-gray-700">Lowest attention - This area is mostly ignored by the model and has little to no effect on the prediction.</span>
      </li>
    </ul>
  </div>
);
export default GradCamGuideline;