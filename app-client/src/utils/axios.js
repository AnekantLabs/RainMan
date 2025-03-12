// creating an axios instance to make api calls
import axios from "axios";

const axiosInstance = axios.create({
    baseURL: "http://localhost:8000/api/v1", // FastAPI backend URL
    headers: {
        "Content-Type": "application/json",
    },
    // withCredentials: true, // Include cookies if using authenticatio
})

// later we can include interceptors for cookies or tokens

export default axiosInstance