import React, { useState, useEffect, useRef } from "react";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import CircularProgress from "@mui/material/CircularProgress";
import TextField from "@mui/material/TextField";
import { useTheme } from "@mui/material/styles";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import AlertService from "services/alertService";

function LogsOverview() {
  const theme = useTheme();
  const [logText, setLogText] = useState(""); // raw JSON text
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [buttonMode, setButtonMode] = useState("edit");

  const pollingInterval = useRef(null);

  const fetchLatestAlert = async () => {
    if (isEditing) return;
    try {
      const alerts = await AlertService.getLatestAlerts();
      if (alerts.length > 0) {
        setLogText(JSON.stringify(alerts[0], null, 2)); // pretty format
      }
    } catch (err) {
      setError("Failed to fetch latest alert.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestAlert();
    pollingInterval.current = setInterval(fetchLatestAlert, 5000);
    return () => clearInterval(pollingInterval.current);
  }, []);

  const handleSend = async () => {
    try {
      const parsed = JSON.parse(logText);
      setSaving(true);
      await AlertService.sendAlert(parsed);
      alert("Alert sent successfully.");
      setIsEditing(false);
      setButtonMode("edit");
      fetchLatestAlert();
    } catch (err) {
      alert("Invalid JSON or failed to send.");
    } finally {
      setSaving(false);
    }
  };

  const handleEditToggle = () => {
    if (buttonMode === "edit") {
      setIsEditing(true);
      clearInterval(pollingInterval.current);
      setButtonMode("get-latest");
    } else {
      setIsEditing(false);
      setButtonMode("edit");
      fetchLatestAlert();
      pollingInterval.current = setInterval(fetchLatestAlert, 5000);
    }
  };

  return (
    <Card
      sx={{
        height: "auto",
        backgroundColor: theme.palette.background.paper,
        borderRadius: "12px",
        boxShadow: 3,
        p: 3,
      }}
    >
      <MDBox
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        px={3}
        py={2}
        sx={{
          backgroundColor: theme.palette.info.main,
          borderRadius: "8px",
        }}
      >
        <MDTypography variant="h6" fontWeight="bold" color="white">
          Alerts Overview 
        </MDTypography>

        <MDBox display="flex" gap={1}>
          <Button
            variant="contained"
            onClick={handleEditToggle}
            disabled={loading}
            sx={{
              fontSize: "0.75rem",
              textTransform: "none",
              fontWeight: "bold",
              backgroundColor:
                buttonMode === "edit"
                  ? theme.palette.info.main
                  : theme.palette.success.main,
              color: "#ffffff",
              "&:hover": {
                backgroundColor:
                  buttonMode === "edit"
                    ? theme.palette.info.dark
                    : theme.palette.success.dark,
              },
            }}
          >
            {buttonMode === "edit" ? "Edit JSON" : "Get Latest"}
          </Button>
          <Button
            variant="contained"
            onClick={handleSend}
            disabled={saving || !logText}
            sx={{
              textTransform: "none",
              fontWeight: "bold",
              padding: "5px 10px",
              fontSize: "0.75rem",
              backgroundColor: theme.palette.error.main,
              color: "#ffffff",
              "&:hover": {
                backgroundColor: theme.palette.error.dark,
              },
            }}
          >
            {saving ? "Sending..." : "Send Alert"}
          </Button>

        </MDBox>
      </MDBox>

      <Divider sx={{ my: 2, bgcolor: "grey.600" }} />

      <MDBox
        sx={{
          backgroundColor: theme.palette.background.default,
          borderRadius: "10px",
          p: 2,
          minHeight: "380px",
          maxHeight: "380px",
          overflowY: "auto",
          boxShadow: 2,
        }}
      >
        {loading ? (
          <MDBox display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress color="info" />
          </MDBox>
        ) : (
          <TextField
            fullWidth
            multiline
            minRows={20}
            maxRows={40}
            value={logText}
            onChange={(e) => {
              setLogText(e.target.value);
              setIsEditing(true);
            }}
            variant="outlined"
            placeholder="Paste JSON here..."
            sx={{
              fontFamily: "monospace",
              backgroundColor: theme.palette.background.paper,
              fontSize: "13px",
            }}
          />
        )}
      </MDBox>
    </Card>
  );
}

export default LogsOverview;
