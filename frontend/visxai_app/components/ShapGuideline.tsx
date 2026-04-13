"use client";
export const ShapGuideline = () => (
  <div className="fixed bottom-2 left-5 bg-white p-3 rounded-lg shadow-md z-10 w-[550px]">
    <h3 className="text-2xl font-semibold text-gray-900 mb-2">SHAP Guideline</h3>
    <p className="text-xl text-gray-700 mb-4">
       SHAP helps explain how your model made a decision by showing which parts (features) of your input had a positive or negative effect on the result.
       There are two key colors: </p>
    <ul className="list-none space-y-3">
      <li className="flex items-center">
        <span className="w-14 h-8 bg-pink-600 mr-2"></span>
        <span className="text-xl text-gray-700"> Features that increase the prediction - These inputs pushed the model toward a higher prediction.</span>
      </li>
      <li className="flex items-center">
        <span className="w-14 h-8 bg-blue-400 mr-2"></span>
        <span className="text-xl text-gray-700"> Features that decrease the prediction - These inputs pushed the model toward a lower prediction.</span>
      </li>
    </ul>

    <ul className="list-none list-inside text-gray-700 space-y-2 mt-4 text-xl">
      <li><strong>Horizontal axis</strong>: This shows how much each input (feature) changes the final prediction, step by step, starting from a base value.</li>
      <li><strong>Vertical axis</strong>: This lists the actual input items the model looked at (like words, measurements).</li>
      <li><strong>Final prediction (f(x))</strong>: This is the model’s final decision after adding up the effects of each input.</li>
      <li><strong>Expected prediction (E[f(X)])</strong>: Think of this as the model’s “average guess” across all data in the input - a neutral starting point.</li>
    </ul>
  </div>
);
export default ShapGuideline;