import React, { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from "@mui/icons-material/Add";
import Modal from "@mui/material/Modal";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { MenuItem } from "@mui/material";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
import accountsTableData from "layouts/accounts/data/accountsTableData";
import axiosInstance from "utils/axios";

function Accounts() {
  const [rows, setRows] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [editedAccount, setEditedAccount] = useState({});
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await axiosInstance.get("api/v1/accounts/get-accounts");
        setRows(response.data);
      } catch (error) {
        console.log(`Error fetching Accounts ${error}`);
      }
    };
    if (!drawerOpen) {
      fetchAccounts(); // Re-fetch data when drawer closes
    }
  }, [drawerOpen]);

  const handleOpenDrawer = (account = null, isNew = false) => {
    setSelectedAccount(account);
    setEditedAccount(
      account
        ? { ...account }
        : {
            account_name: "",
            role: "main",  // ✅ Explicit default
            api_key: "",
            api_secret: "",
            risk_percentage: "",
            leverage: "",
            is_activate: true,
          }
    );
    setIsNew(isNew);
    setDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setDrawerOpen(false);
  };

  const handleSave = async () => {
    try {
      let updatedRows;
      if (isNew) {
        const response = await axiosInstance.post("api/v1/accounts/create-account", editedAccount);
        updatedRows = [
          ...rows,
          {
            ...response.data,
            is_activate: response.data.is_activate === "true",
          },
        ];
      } else {
        await axiosInstance.put(`api/v1/accounts/update-account/${selectedAccount.id}`, editedAccount);
        updatedRows = rows.map((acc) =>
          acc.id === selectedAccount.id
            ? {
                ...editedAccount,
                is_activate: editedAccount.is_activate === "true",
              }
            : acc
        );
      }

      setRows(updatedRows);
      setDrawerOpen(false);
    } catch (error) {
      console.error("Error saving account:", error);
    }
  };

  const tableData = accountsTableData(rows, handleOpenDrawer);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
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
                  Accounts Table
                </MDTypography>
              </MDBox>
              <MDBox pt={3} sx={{ overflowX: "hidden", width: "100%" }}>
                <DataTable
                  table={tableData}
                  isSorted={false}
                  entriesPerPage={false}
                  showTotalEntries={false}
                  noEndBorder
                  sx={{
                    width: "100%",
                    "& .MuiTable-root": { tableLayout: "fixed" },
                    "& .MuiTableCell-root": {
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    },
                  }}
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>

        {/* Enhanced Add Button */}
        <MDButton
          variant="gradient"
          color="info"
          startIcon={<AddIcon />}
          sx={{
            mt: 4,
            px: 4,
            py: 1.5,
            fontSize: "1rem",
            fontWeight: "bold",
            borderRadius: "8px",
            transition: "all 0.2s ease-in-out",
            "&:hover": {
              transform: "scale(1.03)",
            },
          }}
          onClick={() => handleOpenDrawer(null, true)}
        >
           Add New Account
        </MDButton>
      </MDBox>
      <Footer />

      {/* Modal Drawer */}
      <Modal open={drawerOpen} onClose={handleCloseDrawer}>
        <MDBox
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: { xs: "90vw", sm: "500px" },
            bgcolor: "background.default",
            borderRadius: "10px",
            boxShadow: 24,
            p: 4,
            color: "text.primary",
          }}
        >
          <MDBox display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <MDTypography variant="h5">
              {isNew ? "Add New Account" : "Edit Account"}
            </MDTypography>
            <IconButton onClick={handleCloseDrawer}>
              <CloseIcon />
            </IconButton>
          </MDBox>

          <Grid container spacing={2}>
            {Object.keys(editedAccount)
              .filter((key) => !["id", "created_at", "last_updated"].includes(key))
              .map((key) => {
                let inputField;

                if (key === "is_activate") {
                  inputField = (
                    <TextField
                      select
                      fullWidth
                      label="Is Activate"
                      value={String(editedAccount[key])}
                      onChange={(e) =>
                        setEditedAccount({
                          ...editedAccount,
                          [key]: e.target.value,
                        })
                      }
                      SelectProps={{
                        IconComponent: ExpandMoreIcon,
                        sx: { bgcolor: "background.paper" },
                      }}
                      sx={{
                        borderRadius: "5px",
                        height: "50px",
                        "& .MuiOutlinedInput-root": {
                          height: "50px",
                          bgcolor: "background.default",
                        },
                      }}
                    >
                      <MenuItem value="true">True</MenuItem>
                      <MenuItem value="false">False</MenuItem>
                    </TextField>
                  );
                } else if (key === "role") {
                  inputField = (
                    <TextField
                      select
                      fullWidth
                      label="Role"
                      value={editedAccount[key] || "main"}
                      onChange={(e) =>
                        setEditedAccount({
                          ...editedAccount,
                          [key]: e.target.value,
                        })
                      }
                      SelectProps={{
                        IconComponent: ExpandMoreIcon,
                        sx: { bgcolor: "background.paper" },
                      }}
                      sx={{
                        borderRadius: "5px",
                        height: "50px",
                        "& .MuiOutlinedInput-root": {
                          height: "50px",
                          bgcolor: "background.default",
                        },
                      }}
                    >
                      <MenuItem value="main">Main Account</MenuItem>
                      <MenuItem value="sub">Sub Account</MenuItem>
                    </TextField>
                  );
                } else {
                  inputField = (
                    <TextField
                      fullWidth
                      label={key.replace("_", " ")}
                      type={["api_key", "api_secret"].includes(key) ? "password" : "text"}
                      value={editedAccount[key] || ""}
                      onChange={(e) =>
                        setEditedAccount({
                          ...editedAccount,
                          [key]: e.target.value,
                        })
                      }
                      sx={{
                        height: "50px",
                        "& .MuiOutlinedInput-root": {
                          height: "50px",
                          bgcolor: "background.default",
                        },
                      }}
                    />
                  );
                }

                return (
                  <Grid item xs={12} key={key}>
                    {inputField}
                  </Grid>
                );
              })}
          </Grid>

          <Button
            variant="contained"
            onClick={handleSave}
            sx={{
              mt: 3,
              width: "100%",
              height: "50px",
              backgroundColor: "#1A73E8", // Brighter blue
              color: "#FFFFFF", // White text for contrast
              fontWeight: "bold",
              fontSize: "1rem",
              textTransform: "none",
              borderRadius: "8px",
              boxShadow: "0px 3px 6px rgba(0, 0, 0, 0.2)",
              transition: "all 0.2s ease-in-out",
              '&:hover': {
                backgroundColor: "#1558b0", // Darker on hover
                transform: "scale(1.02)",
              },
            }}
          >
            {isNew ? "➕ Add Account" : "💾 Save Changes"}
          </Button>
        </MDBox>
      </Modal>
    </DashboardLayout>
  );
}

export default Accounts;
