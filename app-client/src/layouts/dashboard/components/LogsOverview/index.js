import React, { useState } from "react";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ReactJson from "react-json-view";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import { useTheme } from "@mui/material/styles";

function LogsOverview() {
  const theme = useTheme(); // Get MUI theme for consistency

  // Sample JSON Log Data
  const [logData, setLogData] = useState({
    account: "sub_3",
    action: "buy",
    leverage: "10",
    symbol: "ETHUSDT",
    entry_price: "30000",
    stop_loss: "29000",
    stop_loss_percentage: "10",
    tps: ["31000", "32000", "33000", "34000"],
    tp_sizes: ["10", "10", "10", "10"],
    risk_percentage: "1",
    commission_percentage: "0.02",
    margin_type: "cross",
  });

  // Handle JSON Edits
  const handleEdit = (edit) => {
    setLogData(edit.updated_src);
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
      {/* Section Header */}
      <MDBox
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        px={3}
        py={2}
        sx={{
          backgroundColor: theme.palette.info.main, // Blue color scheme
          borderRadius: "8px",
        }}
      >
        <MDTypography variant="h6" fontWeight="bold" color="white">
          Logs Overview
        </MDTypography>
        <Button
          variant="contained"
          color="white" // Standard button color
          sx={{
            textTransform: "none",
            fontWeight: "bold",
            boxShadow: "none",
            padding: "5px 10px",
            fontSize: "0.75rem",
            color: "#1A73E8",
          }}
        >
          Save Changes
        </Button>
      </MDBox>

      <Divider sx={{ my: 2, bgcolor: "grey.600" }} />

      {/* JSON Viewer Section */}
      <MDBox
        sx={{
          backgroundColor: theme.palette.background.default,
          borderRadius: "10px",
          p: 3,
          minHeight: "380px", // Increased box size
          maxHeight: "380px",
          overflowY: "auto",
          boxShadow: 2,
        }}
      >
        <ReactJson
          src={logData}
          theme="rjv-default" // Standard JSON color scheme
          enableClipboard={true}
          displayDataTypes={false}
          onEdit={handleEdit}
          onAdd={handleEdit}
          onDelete={handleEdit}
          style={{
            fontSize: "12px",
            borderRadius: "8px",
            backgroundColor: theme.palette.background.paper,
            padding: "12px",
            color: theme.palette.text.primary, // Matches the dashboard's text color
          }}
        />
      </MDBox>
    </Card>
  );
}

export default LogsOverview;
