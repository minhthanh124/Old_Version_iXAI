"use client";
import React, { useState, ChangeEvent } from "react";
import {updateFilePathLocalStorage} from '@/shared/module';

import {
  SESSION_ID,
} from '@/shared/constant';

interface FileUploaderProps {
  title: string;
  label: string;
  accept: string;
  description: string;
  onUpload: (file: File[]) => void;
}

interface DataUploaderProps {
  title: string;
  label: string;
  accept: string;
  description: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({ title, label, accept, description, onUpload }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<string>("");

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileArray = Array.from(files);
      setSelectedFiles(fileArray);
      await handleUpload(fileArray);  
    }

  };

  const handleUpload = async (files: File[]) => {
    setStatus("File Uploading ...");
    if (files.length === 0) {
      setStatus("No file selected.");
      return;
    }

    try {
      await onUpload(files);
      setStatus("File uploaded successfully.");
    } catch (error: any) {
      setStatus(error.message);
      setSelectedFiles([]);
    }
  };

  return (
    <div className="w-full mb-5">
        <h3 className="text-2xl font-semibold text-gray-900 inline-block mr-2">{title}</h3>
        <span className="text-blue-500 text-2xl cursor-help inline-block mb-2" title={description}>ℹ️</span>
        <p className="text-xl text-gray-500 mb-2">{label}</p>
        
      <div className="flex items-center justify-between px-1.5 py-1 bg-white border border-gray-300 rounded-md">
          <label className="cursor-pointer text-xl text-blue-600 hover:underline">
              {selectedFiles.length > 0
            ? `${selectedFiles.map(file => file.name).join(', ')}`
            : "Choose file"}
            <input
              type="file"
              accept={accept}
              className="hidden"
              multiple
              onChange={handleFileChange}
            />
          </label>
      </div>
      {status && (
        <p className="mt-2 text-xl text-gray-500">{status}</p>
      )}
    </div>
  );
};

// Export individual uploaders
export const Dataset_Uploader : React.FC<DataUploaderProps> = ({title, label, accept, description}) => {
  const uploadDatasetToBackend = async (files: File[]) => {
    const formData = new FormData();
    const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
    const modalityName = sessionMap[SESSION_ID]?.modality;
    const taskName = sessionMap[SESSION_ID]?.task;
    localStorage.setItem("SessionDataChanged", "true");
    localStorage.removeItem("SessionSelectedLayer");
    localStorage.removeItem("SessionSelectedObject");
    files.forEach((file) => {
      formData.append("files", file);
    });

    formData.append("modality", modalityName);
    formData.append("task", taskName);
    formData.append("data_type", "Dataset");

    const response = await fetch("http://localhost:8001/gateway-service/upload/post/data/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (response.status !== 200) {
      throw new Error(data.message || "Upload failed");
    }
    updateFilePathLocalStorage(SESSION_ID, modalityName, data.message, undefined, undefined, undefined);
  };

  return (
    <FileUploader
      title={title}
      label={label}
      accept={accept}
      description={description}
      onUpload={uploadDatasetToBackend}
    />
  );
};

export const ModelUploader : React.FC<DataUploaderProps> = ({title, label, accept, description}) => {
  const uploadModelToBackend = async (files: File[]) => {
    const formData = new FormData();
    const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
    const modalityName = sessionMap[SESSION_ID]?.modality;
    const taskName = sessionMap[SESSION_ID]?.task;
    localStorage.setItem("SessionDataChanged", "true");
    localStorage.removeItem("SessionSelectedLayer");
    localStorage.removeItem("SessionSelectedObject");
    files.forEach((file) => {
      formData.append("files", file);
    });

    formData.append("modality", modalityName);
    formData.append("task", taskName);
    formData.append("data_type", "Model");

    const response = await fetch("http://localhost:8001/gateway-service/upload/post/data/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (response.status !== 200) {
      throw new Error(data.message || "Upload failed");
    }
    updateFilePathLocalStorage(SESSION_ID, modalityName, undefined, data.message, undefined, undefined);
  };

  return (
    <FileUploader
      title={title}
      label={label}
      accept={accept}
      description={description}
      onUpload={uploadModelToBackend}
    />
  );
};

export const LabelUploader : React.FC<DataUploaderProps> = ({title, label, accept, description}) => {
  const uploadLabelToBackend = async (files: File[]) => {
    const formData = new FormData();
    const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
    const modalityName = sessionMap[SESSION_ID]?.modality;
    const taskName = sessionMap[SESSION_ID]?.task;
    localStorage.setItem("SessionDataChanged", "true");
    localStorage.removeItem("SessionSelectedObject");
    files.forEach((file) => {
      formData.append("files", file);
    });

    formData.append("modality", modalityName);
    formData.append("task", taskName);
    formData.append("data_type", "Label");

    const response = await fetch("http://localhost:8001/gateway-service/upload/post/data/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (response.status !== 200) {
      throw new Error(data.message || "Upload failed");
    }
    updateFilePathLocalStorage(SESSION_ID, modalityName, undefined, undefined, data.message, undefined);
  };

  return (
    <FileUploader
      title={title}
      label={label}
      accept={accept}
      description={description}
      onUpload={uploadLabelToBackend}
    />
  );
};

export const TokenizerUploader : React.FC<DataUploaderProps> = ({title, label, accept, description}) => {
  const uploadTokenizerToBackend = async (files: File[]) => {
    const formData = new FormData();
    const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
    const modalityName = sessionMap[SESSION_ID]?.modality;
    const taskName = sessionMap[SESSION_ID]?.task;

    files.forEach((file) => {
      formData.append("files", file);
    });

    formData.append("modality", modalityName);
    formData.append("task", taskName);
    formData.append("data_type", "Tokenizer");

    const response = await fetch("http://localhost:8001/gateway-service/upload/post/data/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (response.status !== 200) {
      throw new Error(data.message || "Upload failed");
    }
    updateFilePathLocalStorage(SESSION_ID, modalityName, undefined, undefined, undefined, data.message);
  };

  return (
    <FileUploader
      title={title}
      label={label}
      accept={accept}
      description={description}
      onUpload={uploadTokenizerToBackend}
    />
  );
};