import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import CircularProgress from "@mui/material/CircularProgress";
import { useTheme } from "@mui/material/styles";

// Rainman React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DataTable from "examples/Tables/DataTable";

// Services
import AccountService from "services/accountService";

// Context
import { useMaterialUIController } from "context";

function Projects() {
  const theme = useTheme();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;
  const navigate = useNavigate();
  
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [menu, setMenu] = useState(null);

  const openMenu = ({ currentTarget }) => setMenu(currentTarget);
  const closeMenu = () => setMenu(null);

  useEffect(() => {
    let isMounted = true;

    const fetchAccounts = async () => {
      try {
        const accountsData = await AccountService.getAccountInfo();

        const enhancedAccounts = accountsData
          .map((account) => {
            const rawBalance = parseFloat(account.wallet_info?.total_wallet_balance || "0");
            return {
              ...account,
              balance: `$${rawBalance.toFixed(2)}`,
              performance: 50, // Fixed value for demo or standard baseline
            };
          })
          .sort((a, b) => a.account_name.localeCompare(b.account_name));

        if (isMounted) setAccounts(enhancedAccounts);
      } catch (error) {
        console.error("Error fetching accounts:", error);
        if (isMounted) setAccounts([]);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchAccounts(); // initial fetch

    const intervalId = setInterval(() => {
      fetchAccounts(); // poll every 5 seconds
    }, 5000);

    return () => {
      isMounted = false;
      clearInterval(intervalId); // cleanup on unmount
    };
  }, []);

  const handleNavigateToAccounts = () => {
    navigate("/accounts");
    closeMenu();
  };

  const handleRefreshData = () => {
    setLoading(true);
    // Trigger a refresh by calling the fetch function
    const fetchAccounts = async () => {
      try {
        const accountsData = await AccountService.getAccountInfo();
        const enhancedAccounts = accountsData
          .map((account) => {
            const rawBalance = parseFloat(account.wallet_info?.total_wallet_balance || "0");
            return {
              ...account,
              balance: `$${rawBalance.toFixed(2)}`,
              performance: 50,
            };
          })
          .sort((a, b) => a.account_name.localeCompare(b.account_name));
        setAccounts(enhancedAccounts);
      } catch (error) {
        console.error("Error fetching accounts:", error);
        setAccounts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAccounts();
    closeMenu();
  };

  const renderMenu = (
    <Menu
      id="simple-menu"
      anchorEl={menu}
      anchorOrigin={{ vertical: "top", horizontal: "left" }}
      transformOrigin={{ vertical: "top", horizontal: "right" }}
      open={Boolean(menu)}
      onClose={closeMenu}
      PaperProps={{
        sx: {
          backgroundColor: darkMode 
            ? theme.palette.background.paper 
            : theme.palette.background.paper,
          color: darkMode ? theme.palette.text.primary : theme.palette.text.primary,
        }
      }}
    >
      <MenuItem onClick={handleNavigateToAccounts}>View All Accounts</MenuItem>
      <MenuItem onClick={handleNavigateToAccounts}>Add New Account</MenuItem>
      <MenuItem onClick={handleRefreshData}>Refresh Data</MenuItem>
    </Menu>
  );

  const data = {
    columns: [
      { Header: "Account", accessor: "account", width: "45%", align: "left" },
      { Header: "Balance", accessor: "balance", align: "center" },
      { Header: "Performance", accessor: "completion", align: "center" },
    ],
    rows: accounts.map((account) => ({
      account: (
        <MDBox display="flex" alignItems="center" lineHeight={1}>
          <Icon
            sx={{
              fontWeight: "bold",
              color: ({ palette: { info } }) => info.main,
              mr: 1,
            }}
          >
            account_circle
          </Icon>
          <MDTypography
            variant="button"
            fontWeight="medium"
            lineHeight={1}
            color={darkMode ? "white" : "text"}
          >
            {account.account_name}
          </MDTypography>
        </MDBox>
      ),
      balance: (
        <MDTypography 
          variant="caption" 
          color={darkMode ? "white" : "text"} 
          fontWeight="medium"
        >
          {account.balance}
        </MDTypography>
      ),
      completion: (
        <MDBox width="8rem" textAlign="left">
          <MDBox
            variant="gradient"
            bgColor={account.performance >= 60 ? "success" : "info"}
            borderRadius="lg"
            display="flex"
            justifyContent="center"
            alignItems="center"
            width={`${account.performance}%`}
            height="8px"
            sx={{
              background: ({ palette: { info, success } }) =>
                `linear-gradient(to right, ${
                  account.performance >= 60 ? success.main : info.main
                }, ${account.performance >= 80 ? success.dark : info.dark})`,
            }}
          />
        </MDBox>
      ),
      account_name: account.account_name, // For row click
    })),
  };

  const handleRowClick = (rowData) => {
    if (rowData && rowData.account_name) {
      navigate(`/account-details/${rowData.account_name}`);
    }
  };

  return (
    <Card
      sx={{
        backgroundColor: darkMode 
          ? theme.palette.background.card 
          : theme.palette.background.paper,
      }}
    >
      <MDBox display="flex" justifyContent="space-between" alignItems="center" p={3}>
        <MDBox>
          <MDTypography 
            variant="h6" 
            gutterBottom
            color={darkMode ? "white" : "text"}
          >
            Accounts
          </MDTypography>
          <MDBox display="flex" alignItems="center" lineHeight={0}>
            <Icon
              sx={{ fontWeight: "bold", color: ({ palette: { info } }) => info.main, mt: -0.5 }}
            >
              done
            </Icon>
            <MDTypography 
              variant="button" 
              fontWeight="regular" 
              color={darkMode ? "white" : "text"}
            >
              &nbsp;<strong>{accounts.length} accounts</strong> traded
            </MDTypography>
          </MDBox>
        </MDBox>
        <MDBox color={darkMode ? "white" : "text"} px={2}>
          <Icon
            sx={{ 
              cursor: "pointer", 
              fontWeight: "bold",
              color: darkMode ? theme.palette.text.primary : theme.palette.text.primary,
            }}
            fontSize="small"
            onClick={openMenu}
          >
            more_vert
          </Icon>
        </MDBox>
        {renderMenu}
      </MDBox>
      <MDBox>
        {loading ? (
          <MDBox display="flex" justifyContent="center" alignItems="center" p={3}>
            <CircularProgress color="info" />
          </MDBox>
        ) : (
          <DataTable
            table={data}
            showTotalEntries={false}
            isSorted={false}
            noEndBorder
            entriesPerPage={false}
            canSearch={false}
            onRowClick={handleRowClick}
          />
        )}
      </MDBox>
    </Card>
  );
}

export default Projects;