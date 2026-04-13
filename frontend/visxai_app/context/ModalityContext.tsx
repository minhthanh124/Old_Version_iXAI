// context/ModalityContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import {
  SESSION_ID,
} from "../shared/constant";

type Modality = {
  id: string;
  name: string;
};

type ModalityContextType = {
  modalities: Modality[];
};

const ModalityContext = createContext<ModalityContextType>({ modalities: [] });

export const ModalityProvider = ({ children }: { children: ReactNode }) => {
  const [modalities, setModalities] = useState<Modality[]>([]);

  useEffect(() => {
    const fetchModalities = async () => {
      try {
        const response = await fetch("http://localhost:8001/gateway-service/modality/get_modality/");
        if (response.status == 200) {
            const data = await response.json();
            setModalities(data);
            localStorage.setItem(SESSION_ID, data);
        }
      } catch (error) {
        console.error("Failed to fetch modalities:", error);
      }
    };

    fetchModalities();
  }, []);

  return (
    <ModalityContext.Provider value={{ modalities }}>
      {children}
    </ModalityContext.Provider>
  );
};

export const useModality = () => useContext(ModalityContext);
