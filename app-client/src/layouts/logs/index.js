import React, { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReactJson from "react-json-view";
import { Button } from "@mui/material";

function Logs() {
  const [logData, setLogData] = useState({
    account: "sub_3",
    action: "buy",
    leverage: "10",
    symbol: "ETHUSDT",
    entry_price: "30000",
    stop_loss: "29000",
    stop_loss_percentage: "10",
    tps: ["31000", "32000", "33000", "34000", "35000", "36000"],
    tp_sizes: ["10", "10", "10", "10", "10", "10"],
    risk_percentage: "1",
    commission_percentage: "0.02",
    margin_type: "cross",
  });

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
                backgroundColor: "white",
              }}
            >
              {/* Header with Dashboard Theme Colors */}
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
                  Logs Viewer
                </MDTypography>
              </MDBox>

              {/* JSON Viewer Box */}
              <MDBox
                p={3}
                sx={{
                  bgcolor: "white", // Light background
                  borderRadius: "12px",
                  overflow: "auto",
                  maxHeight: "500px",
                  boxShadow: "0px 2px 6px rgba(0, 0, 0, 0.1)", // Soft shadow
                  border: "1px solid #ddd", // Subtle border for clarity
                }}
              >
                <ReactJson
                  src={logData}
                  theme="rjv-default" // Lighter theme
                  onEdit={(edit) => setLogData(edit.updated_src)}
                  onAdd={(add) => setLogData(add.updated_src)}
                  onDelete={(del) => setLogData(del.updated_src)}
                  collapsed={false}
                  enableClipboard={true}
                  displayDataTypes={false}
                  style={{
                    fontSize: "12px", // Same as other dashboard text
                    padding: "12px",
                    borderRadius: "8px",
                  }}
                />
              </MDBox>

              {/* Save Button (Matching Dashboard Styling) */}
              <MDBox display="flex" justifyContent="flex-end" p={3}>
                <Button
                  variant="contained"
                  color="white" // Standard button color
                  sx={{
                    textTransform: "none",
                    fontWeight: "bold",
                    boxShadow: "none",
                    padding: "6px 12px",
                    fontSize: "0.75rem",
                    color: "#1A73E8",
                  }}
                >
                  Save Changes
                </Button>
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
