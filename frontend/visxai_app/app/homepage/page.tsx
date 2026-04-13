'use client'
import Head from "next/head";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation"; // for App Router
import { useModality } from '@/context/ModalityContext';
import { useTask } from '@/context/TaskContext';
import {HomeTabPanel} from "@/components/HomeTabPanel";

const HomePage: React.FC = () => {
  const router = useRouter();
  const { modalities } = useModality();
  const { tasks } = useTask();
  useEffect(() => {
    localStorage.removeItem("SessionFilePath");
    localStorage.removeItem("SessionMethod");
    localStorage.removeItem("SessionSelectedLayer");
    localStorage.removeItem("SessionSelectedObject");
    if (modalities.length > 0) {
      localStorage.setItem("Modality", JSON.stringify(modalities));
    }

    if (tasks.length > 0) {
      localStorage.setItem("Tasks", JSON.stringify(tasks));
    }
  }, [modalities, tasks]);

  return (
    <>
      <Head>
        <title>iXAI</title>
      </Head>
      <div className="min-h-screen bg-white px-6 py-2">
        <HomeTabPanel/>
        {/* Main Content */}
        <main className="text-left">
          <div className="mt-12 border-t border-gray-300 pt-8">
            <p className="text-xl text-blue-600 italic mb-10">
              💡This application helps you understand how an AI made a decision - for an image, a text, or a table.<br/> Just upload your files and we’ll show you a visual explanation.
            </p>
          </div>

          {/* Step-by-Step Guide */}
          <div className="mt-12 border-t border-gray-300 pt-8">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4">🧩 How to get started:</h3>
            <ol className="list-decimal list-inside text-gray-700 space-y-2 text-xl">
              <li><strong> Choose your data type:</strong> Image, Text, or Table.</li>
              <li><strong> Upload your model and input file.</strong></li>
              <li><strong> See a clear explanation</strong> of the AI prediction.</li>
            </ol>
          </div>

          <div className="mt-12 border-t border-gray-300 pt-8">
            <p className="text-xl text-gray-600 italic mb-10">
              🚀 First, choose the type of data you want to explore with AI explanations. Click one to get started:
            </p>
          </div>

          <div className="flex justify-center">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-100">
              <button
                onClick={() => router.push("/modality/computer-vision")}
                className="w-80 h-60 px-6 py-6 bg-purple-600 text-white font-bold py-10 rounded-xl text-xl shadow hover:bg-purple-700">
                <strong className="text-4xl">Images</strong><br /><br />
                <p className="text-1xl font-normal text-white text-center leading-tight">
                  Understand what parts of an image influenced the AI’s decision
                </p>
              </button>
              <button 
                onClick={() => router.push("/modality/nlp")}
                className="w-80 h-60 px-6 py-6 bg-green-600 text-white font-bold py-10 rounded-xl text-xl shadow hover:bg-green-700">
                <strong className="text-4xl">Texts</strong><br /><br />
                <p className="text-1xl font-normal text-white text-center leading-tight">
                  See which words were important for the model’s prediction
                </p>
              </button>

              <button 
                onClick={() => router.push("/modality/tabular")}
                className="w-80 h-60 px-6 py-6 bg-pink-500 text-white font-bold py-10 rounded-xl text-xl shadow hover:bg-pink-600">
                <strong className="text-4xl">Structured Data</strong><br /><br />
                <p className="text-1xl font-normal text-white text-center leading-tight">
                  Learn which data columns affected the model’s outcome
                </p>
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  );
};

export default HomePage;
