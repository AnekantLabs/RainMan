// creating an axios instance to make api calls
import axios from "axios";

// Get API URL from environment variables or fallback to localhost
const API_URL = process.env.REACT_APP_BACKEND_BASE_URL || "http://localhost:8000/api/v1";

const axiosInstance = axios.create({
  baseURL: API_URL, // FastAPI backend URL
  headers: {
    "Content-Type": "application/json",
  },
  // withCredentials: true, // Include cookies if using authentication
});

// Add request interceptor to handle authentication or other common headers
axiosInstance.interceptors.request.use(
  (config) => {
    // You can add authentication tokens or other headers here
    // const token = localStorage.getItem('token');
    // if (token) {
    //    config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle common error cases
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle different error states (401, 403, 500, etc.)
    if (error.response) {
      const { status } = error.response;

      // Log the error for debugging
      console.error(`API Error (${status}):`, error.response.data);

      // Handle specific error statuses
      // if (status === 401) {
      //    // Redirect to login or refresh token
      // }
    } else if (error.request) {
      // The request was made but no response was received
      console.error("Network Error:", error.request);
    } else {
      // Something happened in setting up the request
      console.error("Request Error:", error.message);
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
