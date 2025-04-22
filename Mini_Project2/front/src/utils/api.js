import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const jobApi = {
  getAllJobs: () => api.get('/jobs/'),
  getJob: (id) => api.get(`/jobs/${id}/`),
  searchJobs: (params) => api.get('/jobs/search/', { params }),
  applyForJob: (jobId, data) => api.post(`/jobs/${jobId}/apply/`, data),
};

export const resumeApi = {
  uploadResume: (formData) => api.post('/resumes/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getResumes: () => api.get('/resumes/'),
  deleteResume: (id) => api.delete(`/resumes/${id}/`),
};

export const authApi = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  getCurrentUser: () => api.get('/auth/user/'),
};

export default api;