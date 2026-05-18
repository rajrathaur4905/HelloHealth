import axios from "axios";

// Base API URL configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Create an Axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    // We only access localStorage on the client side
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("accessToken");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s and Errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle Unauthorized errors (e.g. expired token)
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        // Clear local storage on 401
        localStorage.removeItem("accessToken");
        localStorage.removeItem("user");
        
        // Don't redirect if we're already on the login page
        if (!window.location.pathname.includes("/auth/login")) {
          window.location.href = "/auth/login?expired=true";
        }
      }
    }
    
    // Standardize error message extraction from FastAPI
    const customMessage = error.response?.data?.error?.message;
    if (customMessage) {
      error.message = customMessage;
    }
    
    return Promise.reject(error);
  }
);
