import { useState } from "react";
import axios from "axios";
import { Button, Box, CircularProgress } from "@mui/material";
import MDBox from "components/MDBox";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

function RestartStrategyButton() {
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState("");

  const handleRestart = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponseMessage("");

    try {
      const response = await axios.post(`${BACKEND_BASE_URL}/api/v1/accounts/send-accounts-to-queue`);
      const msg = response.data.message || "Strategy restarted.";
      setResponseMessage(msg);
      alert("✅ " + msg);
    } catch (error) {
      const msg = error?.response?.data?.detail || "Failed to restart strategy.";
      setResponseMessage(msg);
      alert("❌ " + msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MDBox mt={1} ml={1}>
      <Box display="flex" justifyContent="flex-end" mt={2} mb={3} ml={1.5}>
        <Button
          variant="contained"
          onClick={handleRestart}
          size="small"
          disabled={loading}
          sx={{
            backgroundColor: "#4caf50",
            color: "#fff",
            minWidth: 90,        // ✅ Make button narrower
            padding: "4px 10px", // ✅ Reduce height & width
            fontSize: "0.75rem", // Same as default small button text
            "&:hover": {
              backgroundColor: "#388e3c",
            },
          }}
        >
          {loading ? (
            <>
              <CircularProgress size={1} sx={{ color: "white", mr: -1 }} />
              Restarting
            </>
          ) : (
            "Fix me"
          )}
        </Button>
      </Box>
    </MDBox>
  );
}

export default RestartStrategyButton;
