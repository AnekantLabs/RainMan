/**
=========================================================
* Rainman React - v2.2.0
=========================================================
*/

import { useState } from "react";
import axios from "axios";

// @mui material components
import { Button, Dialog, DialogActions, DialogContent, DialogTitle,Box } from "@mui/material";

// Rainman React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

function RestartStrategyButton() {
  const [openDialog, setOpenDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState("");

  const handleRestartClick = () => {
    setOpenDialog(true);
  };

  const handleCancel = () => {
    setOpenDialog(false);
    setResponseMessage("");
  };

  const handleConfirm = async () => {
    setLoading(true);
    setResponseMessage("");

    try {
      const response = await axios.post(`${BACKEND_BASE_URL}/api/v1/accounts/send-accounts-to-queue`);
      setResponseMessage(response.data.message || "Strategy restarted.");
    } catch (error) {
      setResponseMessage(
        error?.response?.data?.detail || "Failed to restart strategy."
      );
    } finally {
      setLoading(false);
      setOpenDialog(false);  // ✅ This closes the dialog after attempt
    }
  };

  return (
    <MDBox mt={1} ml={1}>
    <Box display="flex" justifyContent="flex-end" mt={2} mb={3} ml={1.5} >
      <Button
        variant="contained"
        color="success"
        onClick={handleRestartClick}
        size="small"
      >
        Fix me
      </Button>
    </Box>

      <Dialog open={openDialog} onClose={handleCancel} sx={{ zIndex: 1300 }}>
        <DialogTitle>
          <MDTypography variant="h6" fontWeight="medium">
            Confirm Restart
          </MDTypography>
        </DialogTitle>
        <DialogContent>
          <MDTypography variant="body2" mb={1}>
            Are you sure you want to restart the strategy? This will reinitialize all active accounts.
          </MDTypography>
          {responseMessage && (
            <MDTypography variant="caption" color="text">
              {responseMessage}
            </MDTypography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancel} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? "Restarting..." : "Restart"}
          </Button>
        </DialogActions>
      </Dialog>
    </MDBox>
  );
}

export default RestartStrategyButton;
