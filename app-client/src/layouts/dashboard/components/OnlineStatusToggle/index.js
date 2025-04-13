/**
=========================================================
* Rainman React - v2.2.0
=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import { useState } from "react";

// @mui material components
import {
  Switch,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
} from "@mui/material";
import { styled } from "@mui/material/styles";

// Rainman React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Styled MUI Switch component
const StyledSwitch = styled(Switch)(({ theme }) => ({
  width: 42,
  height: 24,
  padding: 0,
  "& .MuiSwitch-switchBase": {
    padding: 0,
    margin: 2,
    transitionDuration: "300ms",
    "&.Mui-checked": {
      transform: "translateX(18px)",
      color: "#fff",
      "& + .MuiSwitch-track": {
        backgroundColor: "rgba(76, 175, 80, 0.2)",
        opacity: 1,
        border: 0,
      },
    },
  },
  "& .MuiSwitch-thumb": {
    width: 17,
    height: 17,
    backgroundColor: "#fff",
  },
  "& .MuiSwitch-track": {
    borderRadius: 24 / 2,
    backgroundColor: "rgba(244, 67, 54, 0.2)",
    opacity: 1,
    transition: theme.transitions.create(["background-color"], {
      duration: 500,
    }),
  },
}));

function OnlineStatusToggle() {
  const [isOnline, setIsOnline] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);

  const handleToggleClick = () => {
    if (isOnline) {
      // If currently online, show confirmation dialog before switching to offline
      setOpenDialog(true);
    } else {
      // If offline, switch to online without confirmation
      setIsOnline(true);
    }
  };

  const handleConfirmOffline = () => {
    setIsOnline(false);
    setOpenDialog(false);
  };

  const handleCancelOffline = () => {
    setOpenDialog(false);
  };

  return (
    <MDBox
      display="flex"
      alignItems="center"
      justifyContent="space-between"
      ml={1}
      sx={{
        border: `1px solid ${
          isOnline ? "rgba(76, 175, 80, 0.2)" : "rgba(244, 67, 54, 0.2)"
        }`,
        borderRadius: "10px",
        padding: "4px 6px",
        backgroundColor: isOnline
          ? "rgba(76, 175, 80, 0.05)"
          : "rgba(244, 67, 54, 0.05)",
        minWidth: "110px",
      }}
    >
      <MDTypography
        variant="caption"
        fontWeight="medium"
        color={isOnline ? "success" : "error"}
      >
        {isOnline ? "On" : "Off"}
      </MDTypography>

      <StyledSwitch
        checked={isOnline}
        onClick={handleToggleClick}
        size="small"
      />

      {/* Confirmation Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCancelOffline}
        sx={{ zIndex: 1300 }}
      >
        <DialogTitle>
          <MDTypography variant="h6" fontWeight="medium">
            Go Offline?
          </MDTypography>
        </DialogTitle>
        <DialogContent>
          <MDTypography variant="body2">
            Turning off the bot will close all open positions at market price.
            Are you sure you want to turn it off?
          </MDTypography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelOffline} color="primary">
            Cancel
          </Button>
          <Button
            onClick={handleConfirmOffline}
            color="error"
            variant="contained"
          >
            Go Offline
          </Button>
        </DialogActions>
      </Dialog>
    </MDBox>
  );
}

export default OnlineStatusToggle;
