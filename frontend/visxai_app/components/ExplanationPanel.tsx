
'use client'

import React, { useEffect, useRef, useState } from 'react'
import {
  SESSION_ID,
  TASK_CLASSIFICATION,
} from '@/shared/constant';
import { useLayerStore, useObjectStore } from '@/shared/store';

const fetchedRequestIds = new Set<number | string>();

type Props = {
  onDone?: () => void
  requestId?: number | string
}

export default function ExplanationResult({ onDone, requestId }: Props) {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false)
  const [nortification, setNortification] = useState(false)
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [htmlOutput, setHtmlOutput] = useState<string | null>(null)
  const [plotOutput, setPlotOutput] = useState<string | null>(null)
  const sessionFilePath = JSON.parse(localStorage.getItem("SessionFilePath") || "{}");
  const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
  const taskName = sessionMap[SESSION_ID]?.task;
  const modality = sessionMap[SESSION_ID]?.modality;
  const method   = localStorage.getItem("SessionMethod");
  const layer    = localStorage.getItem("SessionSelectedLayer");
  const object   = localStorage.getItem("SessionSelectedObject");
  const data_change = localStorage.getItem("SessionDataChanged");
  const { setLayers } = useLayerStore();
  const { setObjects } = useObjectStore();
  const dataset_path = sessionFilePath?.[SESSION_ID]?.[modality]?.dataset;
  const model_path = sessionFilePath?.[SESSION_ID]?.[modality]?.model;
  const label_path = sessionFilePath?.[SESSION_ID]?.[modality]?.label;
  const tokenizer_path = sessionFilePath?.[SESSION_ID]?.[modality]?.tokenizer;
  
  const [description, setDescription] = useState<string | null>(null)
  const hasFetchedRef = useRef(false)
  const isFetchingRef = useRef(false)

  useEffect(() => {
    const container = document.getElementById("shap-container");
    const scripts = container?.getElementsByTagName("script");
    if (scripts) {
      Array.from(scripts).forEach((script) => {
        const newScript = document.createElement("script");
        newScript.text = script.text;
        document.body.appendChild(newScript);
      });
    }
  }, [htmlOutput]);

  function parseDescription(desc: string) {
    const lines = desc.split('\n');
    const parsed: Record<string, string> = {};
    lines.forEach(line => {
      const [key, ...rest] = line.split(':');
      if (key && rest.length > 0) {
        parsed[key.trim()] = rest.join(':').trim();
      }
    });
    return parsed;
  }

  function renderDescription(desc: string) {
    const parsedDesc = parseDescription(desc);
    const entries = Object.entries(parsedDesc);

    if (entries.length > 0) {
      return (
        <div>
          {entries.map(([key, val]) => (
            <p key={key}><strong>{key}:</strong> {val}</p>
          ))}
        </div>
      );
    }

    return <p className="whitespace-pre-line">{desc}</p>;
  }

  const fetchGradCam = async () => {
    if (isFetchingRef.current) return
    isFetchingRef.current = true
    setLoading(true)
    setNortification(false)
    setStatus("Generating explanation...")
    const payload: Record<string, any> = {
      modality: modality,
      task: taskName,
      method: method,
    };

    if (dataset_path) payload.dataset_path = dataset_path;
    if (model_path) payload.model_path = model_path;
    if (TASK_CLASSIFICATION.includes(taskName)) {
      if (label_path) payload.label_path = label_path;
    }
    if (modality == "Natural Language Processing") {
      if (tokenizer_path) payload.tokenizer_path = tokenizer_path;
    }
    if (modality == "Computer Vision") {
      if (layer) {
        payload.layer = layer;
      }
      if (object) {
        payload.object = object;
      }
    }

    try {
        const response = await fetch('http://localhost:8001/gateway-service/explanation/post/explanation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payload
        }),
        })

        const data = await response.json()
        if (response.status !== 200) {
          setNortification(true)
          setStatus(data.result)
          throw new Error(data.result);
        }

        if (data.result?.image_base64) {
            setResultImage(data.result.image_base64);
        }

        if (data.description) {
            setDescription(data.description);
        }

        if (data_change == "true") {
          if (modality == "Computer Vision" && data.extra_data) {
            setLayers(data.extra_data?.cnn_layer);
            setObjects(data.extra_data?.target_classes);
            localStorage.setItem("SessionDataChanged", "false");
          }
        }

        if (data.result?.html_str) {
          setHtmlOutput(data.result.html_str)
        }

        if (data.result?.plot_waterfall) {
          setPlotOutput(data.result.plot_waterfall)
        }
      
    } catch (error: any) {
      setStatus(error.message)
    } finally {
      isFetchingRef.current = false
      setLoading(false)
    }
  }

  useEffect(() => {
    const currentRequestId = requestId ?? 'default'
    if (fetchedRequestIds.has(currentRequestId)) return
    fetchedRequestIds.add(currentRequestId)
    fetchGradCam()
  }, [requestId]);

  return (
    <div className="p-6 bg-white rounded-xl shadow-md w-full">
      <h2 className="text-3xl font-bold mb-4 text-center">Result</h2>

      {loading && <p className="text-center text-xl text-gray-500">Generating explanation...</p>}
      {nortification && <p className="text-center text-xl text-gray-500">{status}</p>}

      {(resultImage || htmlOutput || plotOutput || description) && (
        <div className="flex flex-col gap-6">
          {resultImage && (
            <div className="flex-shrink-0">
              <img
                src={`data:image/png;base64,${resultImage}`}
                alt="Grad-CAM"
                className="rounded-lg border w-[350px] h-auto object-contain"
              />
            </div>
          )}

          {description && (
            <div className="text-lg text-gray-700 w-full">
              <h3 className="text-2xl font-semibold mb-2">Explanation</h3>
              {renderDescription(description)}
            </div>
          )}
        </div>
      )}
          {htmlOutput && (
            <div
              className="rounded-lg border p-4 max-w-full overflow-auto"
              id="shap-container"
              dangerouslySetInnerHTML={{ __html: htmlOutput }}
            />
          )}

          {plotOutput && (
            <div className="flex justify-center">
            <div className="rounded-lg border p-4 max-w-full overflow-auto">
              <img
                  src={`data:image/png;base64,${plotOutput}`}
                  alt="Plot Output"
                  className="mx-auto"
              />
            </div>
            </div>   
          )}
    </div>
  )
}
