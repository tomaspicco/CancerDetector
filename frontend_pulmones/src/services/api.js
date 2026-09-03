import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

export const uploadZipFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  // Es vital retornar response.data para que el Dashboard reciba el task_id
  return response.data; 
};

export const checkTaskStatus = async (taskId) => {
  const response = await apiClient.get(`/api/status/${taskId}`);
  return response.data;
};