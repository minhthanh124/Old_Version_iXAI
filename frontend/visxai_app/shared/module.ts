// interface ModalityTask {
//   modality_id: string;
//   task_id: string;
// }

// type UserData = Record<string, ModalityTask[]>;

// export const readFromLocalStorage = (key: string) => {
//   if (typeof window === "undefined") {
//     console.warn("localStorage is not available on the server.");
//     return null;
//   }

//   try {
//     const item = localStorage.getItem(key);
//     return item;
//   } catch (error) {
//     console.error(`Error reading key "${key}" from localStorage:`, error);
//     return null;
//   }
// };

// export function addUserModalityTask(sessionId: string, modalityId: string, taskId: string): void {
//   const userDataStr = localStorage.getItem("userData");
//   const allUserData: UserData = userDataStr ? JSON.parse(userDataStr) : {};

//   if (!allUserData[sessionId]) {
//     allUserData[sessionId] = [];
//   }

//   allUserData[sessionId].push({
//     modality_id: modalityId,
//     task_id: taskId,
//   });

//   localStorage.setItem("userData", JSON.stringify(allUserData));
// }

// export function getUserModalityTasks(sessionId: string): ModalityTask[] {
//   const userDataStr = localStorage.getItem("userData");
//   const allUserData: UserData = userDataStr ? JSON.parse(userDataStr) : {};
//   return allUserData[sessionId] || [];
// }

// interface SessionData {
//   modality: string;
//   task: string;
// }

export function updateModalityLocalStorage(sessionId: string, modality_name: string, task_name: string): void {
  const sessionMap = JSON.parse(localStorage.getItem("SessionMap") || "{}");
  sessionMap[sessionId] = {
    modality: modality_name,
    task: task_name,
  };
    localStorage.setItem("SessionMap", JSON.stringify(sessionMap));
}

export function updateFilePathLocalStorage(
  sessionId: string,
  modality: string,
  dataset_path?: string,
  model_path?: string,
  label_path?: string,
  tokenizer_path?: string
): void {
  const sessionFilePath = JSON.parse(localStorage.getItem("SessionFilePath") || "{}");
  const current = sessionFilePath[sessionId] || {};
  const taskData = current[modality] || {};
  current[modality] = {
    // modality: modality,
    dataset: dataset_path !== undefined ? dataset_path : taskData.dataset,
    model: model_path !== undefined ? model_path : taskData.model,
    label: label_path !== undefined ? label_path : taskData.label,
    tokenizer: tokenizer_path !== undefined ? tokenizer_path : taskData.tokenizer
  };
  sessionFilePath[sessionId] = current;

  localStorage.setItem("SessionFilePath", JSON.stringify(sessionFilePath));

  // sessionFilePath[sessionId] = {
  //   task: task,
  //   dataset: dataset_path !== undefined ? dataset_path : current.dataset,
  //   model: model_path !== undefined ? model_path : current.model,
  //   label: label_path !== undefined ? label_path : current.label,
  //   tokenizer: tokenizer_path !== undefined ? tokenizer_path : current.tokenizer
  // };

  // localStorage.setItem("SessionFilePath", JSON.stringify(sessionFilePath));
}