import React, { useEffect, useState, useRef } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import { useTheme } from "@mui/material/styles";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import { useMaterialUIController } from "context";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_BASE_URL;

function Logs() {
  const theme = useTheme();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;
  
  const [logs, setLogs] = useState([]);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    const source = new EventSource(`${BACKEND_BASE_URL}/api/v1/alerts/logs/stream`);
    eventSourceRef.current = source;

    source.addEventListener("log", (event) => {
      try {
        const log = JSON.parse(event.data);
        setLogs((prevLogs) => {
          const updated = [...prevLogs, log];  // <-- Append to end (oldest at top)
          return updated.slice(-100);          // Keep max 100 logs
        });
      } catch (e) {
        console.error("Invalid JSON log:", e);
      }
    });

    source.onerror = (error) => {
      console.error("SSE error:", error);
      source.close();
    };

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        console.log("🔌 SSE connection closed.");
      }
    };
  }, []);

  const getChipColor = (level) => {
    switch (level) {
      case "ERROR":
        return "error";
      case "WARNING":
        return "warning";
      case "DEBUG":
        return "secondary";
      default:
        return "info";
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={6} px={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card
              sx={{
                boxShadow: 2,
                borderRadius: "12px",
                backgroundColor: darkMode 
                  ? theme.palette.background.card 
                  : "white",
              }}
            >
              {/* Header */}
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Logs Viewer (Live)
                </MDTypography>
              </MDBox>

              {/* Logs Output */}
              <MDBox
                p={3}
                sx={{
                  bgcolor: darkMode 
                    ? theme.palette.background.default 
                    : "#f9fafc",
                  borderRadius: "12px",
                  overflow: "auto",
                  maxHeight: "75vh",
                  fontFamily: "monospace",
                  fontSize: "12px",
                  lineHeight: "1.5",
                }}
              >
                {logs.length === 0 ? (
                  <MDTypography 
                    variant="body2" 
                    color={darkMode ? "white" : "textSecondary"}
                  >
                    Waiting for logs...
                  </MDTypography>
                ) : (
                  logs.map((log, idx) => (
                    <MDBox
                      key={idx}
                      display="flex"
                      alignItems="center"
                      justifyContent="space-between"
                      sx={{
                        borderBottom: darkMode 
                          ? "1px solid #444" 
                          : "1px solid #eee",
                        paddingY: "6px",
                        "&:hover": {
                          backgroundColor: darkMode 
                            ? "rgba(255, 255, 255, 0.08)" 
                            : "#eef2f6",
                        },
                      }}
                    >
                      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                        <Chip
                          label={log.level}
                          size="small"
                          color={getChipColor(log.level)}
                          variant="filled"
                        />
                        <MDTypography 
                          variant="caption" 
                          color={darkMode ? "white" : "text"} 
                          fontWeight="medium"
                        >
                          {log.timestamp}
                        </MDTypography>
                      </Stack>
                      <MDTypography
                        variant="caption"
                        color={darkMode ? "white" : "text"}
                        sx={{
                          ml: 2,
                          flex: 1,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {log.message}
                      </MDTypography>
                    </MDBox>
                  ))
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Logs;