/**
=========================================================
* Rainman React - v2.2.0
=========================================================
*/

import { useState } from "react";
import axios from "axios";

// @mui material components
import { Button, Box } from "@mui/material";

// Rainman React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

function RestartStrategyButton() {
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState("");

  const handleRestart = async () => {
    setLoading(true);
    setResponseMessage("");

    try {
      const response = await axios.post(`${BACKEND_BASE_URL}/api/v1/accounts/send-accounts-to-queue`);
      setResponseMessage(response.data.message || "Strategy restarted.");
      alert("✅ " + (response.data.message || "Strategy restarted."));
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
            backgroundColor: "#4caf50",        // Material Green 500
            color: "#fff",
            "&:hover": {
              backgroundColor: "#388e3c",      // Darker green on hover
            },
          }}
        >
          {loading ? "Restarting..." : "Fix me"}
        </Button>
      </Box>
    </MDBox>
  );
}

export default RestartStrategyButton;
