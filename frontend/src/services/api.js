import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const trainModel = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/train', formData);
  return response.data;
};

export const runInference = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/inference', formData);
  return response.data;
};

export const downloadFile = (filename) => {
  return `${API_BASE_URL}/api/download/${filename}`;
};

export const getTrainingStatus = async () => {
  const response = await api.get('/api/training-status');
  return response.data;
};

export const previewPipeline = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/preview-pipeline', formData);
  return response.data;
};

export const getTrainingPreview = async (filename) => {
  const response = await api.get(`/api/training-preview/${encodeURIComponent(filename)}`);
  return response.data;
};

export const getInferenceProgress = async (jobId) => {
  const response = await api.get(`/api/inference/progress/${jobId}`);
  return response.data;
};

