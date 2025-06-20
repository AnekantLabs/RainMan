import React, { useState, useEffect, useRef } from "react";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import CircularProgress from "@mui/material/CircularProgress";
import { useTheme } from "@mui/material/styles";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ReactJson from "react-json-view";
import AlertService from "services/alertService";

function LogsOverview() {
  const theme = useTheme();
  const [logData, setLogData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false); // true when user has toggled edit mode
  const [buttonMode, setButtonMode] = useState("edit"); // "edit" or "get-latest"

  const pollingInterval = useRef(null);

  const fetchLatestAlert = async () => {
    if (isEditing) return;
    try {
      const alerts = await AlertService.getLatestAlerts();
      if (alerts.length > 0) setLogData(alerts[0]);
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

  const handleJsonChange = (change) => {
    if (change.updated_src) {
      setLogData(change.updated_src);
    }
  };

  const handleSend = async () => {
    if (!logData || typeof logData !== "object") return alert("Invalid JSON");

    setSaving(true);
    try {
      await AlertService.sendAlert(logData);
      alert("Alert sent successfully.");
      setIsEditing(false);
      setButtonMode("edit");
      fetchLatestAlert(); // optionally refresh
    } catch (err) {
      console.error("Failed to send alert:", err);
      alert("Failed to send alert.");
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

  const renderJsonViewer = () => {
    if (loading) {
      return (
        <MDBox display="flex" justifyContent="center" alignItems="center" height="200px">
          <CircularProgress color="info" />
        </MDBox>
      );
    }

    if (error) {
      return (
        <MDTypography color="error" fontWeight="medium">
          {error}
        </MDTypography>
      );
    }

    if (!logData) {
      return (
        <MDTypography variant="body2" fontWeight="medium">
          No alert found.
        </MDTypography>
      );
    }

    return (
      <ReactJson
        src={logData}
        theme="rjv-default"
        enableClipboard={true}
        displayDataTypes={false}
        onEdit={handleJsonChange}
        onAdd={handleJsonChange}
        onDelete={handleJsonChange}
        style={{
          fontSize: "12px",
          borderRadius: "8px",
          backgroundColor: theme.palette.background.paper,
          padding: "12px",
          color: theme.palette.text.primary,
        }}
      />
    );
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
          Logs Overview (Live + Editable)
        </MDTypography>

        <MDBox display="flex" gap={1}>
          <Button
            variant="outlined"
            color={buttonMode === "edit" ? "secondary" : "primary"}
            onClick={handleEditToggle}
            disabled={loading}
            sx={{
              fontSize: "0.75rem",
              textTransform: "none",
              fontWeight: "bold",
            }}
          >
            {buttonMode === "edit" ? "Edit JSON" : "Get Latest"}
          </Button>

          <Button
            variant="contained"
            onClick={handleSend}
            disabled={saving || !logData}
            sx={{
              textTransform: "none",
              fontWeight: "bold",
              boxShadow: "none",
              padding: "5px 10px",
              fontSize: "0.75rem",
              color: "#1A73E8",
              backgroundColor: "#ffffff",
              "&:hover": {
                backgroundColor: "#f0f0f0",
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
          p: 3,
          minHeight: "380px",
          maxHeight: "380px",
          overflowY: "auto",
          boxShadow: 2,
        }}
      >
        {renderJsonViewer()}
      </MDBox>
    </Card>
  );
}

export default LogsOverview;
