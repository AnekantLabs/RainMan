import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  const [isValid, setIsValid] = useState(null);

  useEffect(() => {
    if (!token) {
      setIsValid(false);
      return;
    }

    axios
      .get("http://localhost:8000/api/v1/users/me", {
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