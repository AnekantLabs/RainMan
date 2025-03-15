
import React, { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
// import Drawer from "@mui/material/Drawer";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from "@mui/icons-material/Add";
import Modal from "@mui/material/Modal";

// Material Dashboard Components
// import MDBadge from "components/MDBadge";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

// Import Data Function
import accountsTableData from "layouts/accounts/data/accountsTableData";
import axiosInstance from "utils/axios";
import { MenuItem } from "@mui/material";

function Accounts() {
    //   const [rows, setRows] = useState([
    //     {
    //       account_name: "subaccount1",
    //       role: "master_account",
    //       api_key: "eyihwqeihioenwcioneanceaec",
    //       api_secret: "eiwheownevoiwneviownevowevni",
    //       risk_percentage: "1%",
    //       leverage: "2%",
    //       is_activate:false,
    //     },
    //     {
    //       account_name: "subaccount2",
    //       role: "standard_account",
    //       api_key: "ajdfj2398fhdshfjdhfjds",
    //       api_secret: "dkjfhsdjhf7328hdsf823h",
    //       risk_percentage: "2%",
    //       leverage: "5%",
    //       is_activate:true,
    //     },
    //   ]);


    const [rows, setRows] = useState([])
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedAccount, setSelectedAccount] = useState(null);
    const [editedAccount, setEditedAccount] = useState({});
    const [isNew, setIsNew] = useState(false);

    // fetch the data from the backend when the component is rendered
    useEffect(() => {
        const fetchAccounts = async () => {
            try {
                const response = await axiosInstance.get('/accounts/get-accounts');
                setRows(response.data);
            } catch (error) {
                console.log(`Error fetching Accounts ${error}`);
            }
        };

        fetchAccounts();
    }, []);      // keep the dependency array empty, only load when the whole component renders


    const handleOpenDrawer = (account = null, isNew = false) => {

        // console.log(`Selected Account Id: ${account.id} ${JSON.stringify(account)}`);

        // selected account is the account to be edited
        setSelectedAccount(account);
        setEditedAccount(
            account
                ? { ...account }
                : {
                    account_name: "",
                    role: "",
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
            if (isNew) {
                // Add a new account via API
                const response = await axiosInstance.post('/accounts/create-account', editedAccount);
                console.log(`New Account: ${JSON.stringify(editedAccount)}`);
                setRows([...rows, response.data]);  // Update table with new data
            } else {
                // Update an existing account
                await axiosInstance.put(`/accounts/update-account/${selectedAccount.id}`, editedAccount);
                console.log(`Edited Account: ${JSON.stringify(editedAccount)}`);
                setRows(rows.map((acc) => (acc.id === selectedAccount.id ? editedAccount : acc)));
            }
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
                            <MDBox mx={2} mt={-3} py={3} px={2} variant="gradient" bgColor="info" borderRadius="lg" coloredShadow="info">
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
                                            textOverflow: "ellipsis"
                                        },
                                    }}
                                />
                            </MDBox>
                        </Card>
                    </Grid>
                </Grid>
                <Button variant="contained" color="primary" startIcon={<AddIcon />} sx={{ marginTop: 2 }} onClick={() => handleOpenDrawer(null, true)}>
                    Add New Account
                </Button>
            </MDBox>
            <Footer />

            {/* Side Drawer for Account Details */}
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
                            .map((key) => (
                                <Grid item xs={12} key={key}>
                                    {/* If field is 'is_activate', render dropdown */}
                                    {key === "is_activate" ? (
                                        <TextField
                                            select
                                            fullWidth
                                            label="Is Activate"
                                            value={String(editedAccount[key]) || "false"} // Default value
                                            onChange={(e) =>
                                                setEditedAccount({ ...editedAccount, [key]: e.target.value })
                                            }
                                        >
                                            <MenuItem value="true">True</MenuItem>
                                            <MenuItem value="false">False</MenuItem>
                                        </TextField>
                                    ) : (
                                        // Render normal text field for other fields
                                        <TextField
                                            fullWidth
                                            label={key.replace("_", " ")}
                                            value={editedAccount[key] || ""}
                                            onChange={(e) =>
                                                setEditedAccount({ ...editedAccount, [key]: e.target.value })
                                            }
                                        />
                                    )}
                                </Grid>
                            ))}
                    </Grid>

                    <Button
                        variant="contained"
                        color="primary"
                        sx={{ mt: 3, width: "100%" }}
                        onClick={handleSave}
                    >
                        {isNew ? "Add Account" : "Save Changes"}
                    </Button>
                </MDBox>
            </Modal>

        </DashboardLayout>
    );
}

export default Accounts;