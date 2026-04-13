"use client";
import React, { useState, useEffect } from "react";
import {updateModalityLocalStorage} from '@/shared/module';
import {
  SESSION_ID,
} from '@/shared/constant';

interface TaskPanelProps {
  modality_name: string;
  task_name: string[];
  onTaskSelect: (selectedTask: string) => void;
  description: { [key: string]: string };
}

export const TaskPanel: React.FC<TaskPanelProps> = ({ modality_name, task_name, onTaskSelect, description}) => {
  const [selectedTask, setSelectedTask] = useState<string>(task_name[0]);
  useEffect(() => {
    updateModalityLocalStorage(SESSION_ID, modality_name, selectedTask);
    onTaskSelect(task_name[0]);
  }, [task_name, onTaskSelect]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    localStorage.setItem("SessionDataChanged", "true");
    localStorage.removeItem("SessionSelectedLayer");
    localStorage.removeItem("SessionSelectedObject");
    const task = e.target.value;
    setSelectedTask(task);
    updateModalityLocalStorage(SESSION_ID, modality_name, task);
    onTaskSelect(task);
  };

  return (
    <div className="w-1/4 pr-4">
      <h2 className="text-2xl font-bold mb-4">{modality_name}</h2>
      <select
        value={selectedTask}
        onChange={handleChange}
        className="text-2xl block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-teal-500"
      >
        {task_name.map((task) => (
          <option key={task} value={task}>
            {task}
          </option>
        ))}
      </select>

      {/* Description */}
      <p className="text-xl mt-6 text-md text-gray-600 italic">
        {description[selectedTask]}
      </p>
    </div>
  );
};

export default TaskPanel;
