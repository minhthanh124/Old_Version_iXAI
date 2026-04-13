// context/TaskContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

type Task = {
  id: string;
  name: string;
  modality: string
};

type TaskContextType = {
  tasks: Task[];
};

const TaskContext = createContext<TaskContextType>({ tasks: [] });

export const TaskProvider = ({ children }: { children: ReactNode }) => {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await fetch("http://localhost:8001/gateway-service/modality/get_task/");
        if (response.status == 200) {
            const data = await response.json();
            setTasks(data);
        }
      } catch (error) {
        console.error("Failed to fetch tasks:", error);
      }
    };

    fetchTasks();
  }, []);

  return (
    <TaskContext.Provider value={{ tasks }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTask = () => useContext(TaskContext);
