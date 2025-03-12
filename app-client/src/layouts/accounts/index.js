import React, { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Drawer from "@mui/material/Drawer";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from "@mui/icons-material/Add";

// Material Dashboard Components
import MDBadge from "components/MDBadge";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

// Import Data Function
import accountsTableData from "layouts/accounts/data/accountsTableData";
import axiosInstance from "utils/axios";

function Accounts() {
    //   const [rows, setRows] = useState([
    //     {
    //       account_name: "subaccount1",
    //       role: "master_account",
    //       api_key: "eyihwqeihioenwcioneanceaec",
    //       api_secret: "eiwheownevoiwneviownevowevni",
    //       risk_percentage: "1%",
    //       leverage: "2%",
    //       is_activate: <MDBadge badgeContent="Active" color="success" variant="gradient" size="sm" />,
    //     },
    //     {
    //       account_name: "subaccount2",
    //       role: "standard_account",
    //       api_key: "ajdfj2398fhdshfjdhfjds",
    //       api_secret: "dkjfhsdjhf7328hdsf823h",
    //       risk_percentage: "2%",
    //       leverage: "5%",
    //       is_activate: <MDBadge badgeContent="Inactive" color="dark" variant="gradient" size="sm" />,
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
                const response = await axiosInstance.get('/accounts/get-accounts')
                setRows(response.data)
                console.log(response.data)
            } catch (error) {
                console.log(`Error fetching Accounts ${error}`)
            }
        }

        fetchAccounts()
    }, [])      // keep the dependency array empty, only load when the whole component renders


    const handleOpenDrawer = (account = null, isNew = false) => {
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

    const handleSave = () => {
        if (isNew) {
            setRows([...rows, { ...editedAccount }]);
        } else {
            setRows(rows.map((acc) => (acc.account_name === selectedAccount.account_name ? editedAccount : acc)));
        }
        setDrawerOpen(false);
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
                            <MDBox pt={3}>
                                <DataTable table={tableData} isSorted={false} entriesPerPage={false} showTotalEntries={false} noEndBorder />
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
            <Drawer anchor="right" open={drawerOpen} onClose={handleCloseDrawer}>
                <MDBox width="400px" p={3}>
                    <MDBox display="flex" justifyContent="space-between" alignItems="center">
                        <MDTypography variant="h5">{isNew ? "Add New Account" : "Edit Account"}</MDTypography>
                        <IconButton onClick={handleCloseDrawer}>
                            <CloseIcon />
                        </IconButton>
                    </MDBox>

                    <Grid container spacing={2} mt={2}>
                        {Object.keys(editedAccount).map((key) => (
                            <Grid item xs={12} key={key}>
                                <TextField fullWidth label={key.replace("_", " ")} value={editedAccount[key] || ""} onChange={(e) => setEditedAccount({ ...editedAccount, [key]: e.target.value })} />
                            </Grid>
                        ))}
                    </Grid>

                    <Button variant="contained" color="primary" sx={{ marginTop: 2 }} fullWidth onClick={handleSave}>
                        {isNew ? "Add Account" : "Save Changes"}
                    </Button>
                </MDBox>
            </Drawer>
        </DashboardLayout>
    );
}

export default Accounts;