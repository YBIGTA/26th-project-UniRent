import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: "http://3.34.99.86:5000/api/users",
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
axiosInstance.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosInstance;
