import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  const [isValid, setIsValid] = useState(null);

  useEffect(() => {
    if (!token) {
      setIsValid(false);
      return;
    }

    axios
      .get(`${BACKEND_BASE_URL}/api/v1/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(() => setIsValid(true))
      .catch(() => setIsValid(false));
  }, [token]);

  if (isValid === null) return <div>Loading...</div>;
  if (!isValid) return <Navigate to="/authentication/sign-in" replace />;
  return children;
}

export default ProtectedRoute;