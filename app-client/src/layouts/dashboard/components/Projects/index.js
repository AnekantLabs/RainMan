/**
=========================================================
* Rainman React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import { useState, useEffect } from "react";
// import { Link } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import CircularProgress from "@mui/material/CircularProgress";

// Rainman React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Rainman React examples
import DataTable from "examples/Tables/DataTable";

// Services
import AccountService from "services/accountService";

function Projects() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [menu, setMenu] = useState(null);

  const openMenu = ({ currentTarget }) => setMenu(currentTarget);
  const closeMenu = () => setMenu(null);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        // Use AccountService to fetch accounts
        const accountsData = await AccountService.getAllAccounts();

        // Fetch metrics for each account
        const accountsWithMetrics = await Promise.all(
          accountsData.map(async (account) => {
            try {
              const metrics = await AccountService.getAccountMetrics(
                account.id
              );
              return {
                ...account,
                balance: metrics.balance || "$0.00",
                performance: metrics.performance || 0,
              };
            } catch (error) {
              console.error(
                `Error fetching metrics for account ${account.id}:`,
                error
              );
              return {
                ...account,
                balance: "$0.00",
                performance: 0,
              };
            }
          })
        );

        setAccounts(accountsWithMetrics);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching accounts:", error);
        // For demo purposes, set mock data if API fails
        setAccounts(getMockAccounts());
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  // Helper to get mock accounts for demo
  const getMockAccounts = () => {
    return [
      {
        id: "1",
        account_name: "Main Account",
        role: "main",
        risk_percentage: "5",
        balance: "$14,000",
        performance: 60,
      },
      {
        id: "2",
        account_name: "Sub Account 1",
        role: "sub",
        risk_percentage: "3",
        balance: "$3,000",
        performance: 10,
      },
      {
        id: "3",
        account_name: "Sub Account 2",
        role: "sub",
        risk_percentage: "7",
        balance: "Not set",
        performance: 100,
      },
      {
        id: "4",
        account_name: "Sub Account 3",
        role: "sub",
        risk_percentage: "2",
        balance: "$20,500",
        performance: 100,
      },
      {
        id: "5",
        account_name: "Sub Account 4",
        role: "sub",
        risk_percentage: "4",
        balance: "$500",
        performance: 25,
      },
    ];
  };

  const handleNavigateToAccounts = () => {
    window.location.href = "/accounts";
    closeMenu();
  };

  const renderMenu = (
    <Menu
      id="simple-menu"
      anchorEl={menu}
      anchorOrigin={{
        vertical: "top",
        horizontal: "left",
      }}
      transformOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      open={Boolean(menu)}
      onClose={closeMenu}
    >
      <MenuItem onClick={handleNavigateToAccounts}>View All Accounts</MenuItem>
      <MenuItem onClick={handleNavigateToAccounts}>Add New Account</MenuItem>
      <MenuItem onClick={closeMenu}>Refresh Data</MenuItem>
    </Menu>
  );

  // Generate table data from accounts
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
            color="text"
          >
            {account.account_name}
          </MDTypography>
        </MDBox>
      ),
      balance: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {account.balance || "$0.00"}
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
      // Add original data needed for row click handler
      id: account.id,
    })),
  };

  const handleRowClick = (rowData) => {
    window.location.href = `/account-details/${rowData.id}`;
  };

  return (
    <Card>
      <MDBox
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        p={3}
      >
        <MDBox>
          <MDTypography variant="h6" gutterBottom>
            Accounts
          </MDTypography>
          <MDBox display="flex" alignItems="center" lineHeight={0}>
            <Icon
              sx={{
                fontWeight: "bold",
                color: ({ palette: { info } }) => info.main,
                mt: -0.5,
              }}
            >
              done
            </Icon>
            <MDTypography variant="button" fontWeight="regular" color="text">
              &nbsp;<strong>{accounts.length} accounts</strong> traded
            </MDTypography>
          </MDBox>
        </MDBox>
        <MDBox color="text" px={2}>
          <Icon
            sx={{ cursor: "pointer", fontWeight: "bold" }}
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
          <MDBox
            display="flex"
            justifyContent="center"
            alignItems="center"
            p={3}
          >
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
