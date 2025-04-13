import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Grid, Card, Tabs, Tab, Box, CircularProgress } from "@mui/material";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DataTable from "examples/Tables/DataTable";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import AccountService from "services/accountService";
import OrderService from "services/orderService";

function AccountDetails() {
  const { accountId } = useParams();
  const [account, setAccount] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  // Helper to get mock orders for demo
  const getMockOrders = () => {
    return [
      {
        id: "1",
        date: "2025-02-26 10:32:08",
        market_pair: "ETH/USDT",
        side: "sell",
        type: "market",
        price: "2200.03",
        amount: "0.000527",
        executed: "100%",
        status: "closed",
      },
      {
        id: "2",
        date: "2025-02-26 10:32:07",
        market_pair: "ETH/USDT",
        side: "buy",
        type: "market",
        price: "3485.72",
        amount: "0.000527",
        executed: "100%",
        status: "closed",
      },
      {
        id: "3",
        date: "2025-02-26 10:31:53",
        market_pair: "ETH/USDT",
        side: "sell",
        type: "market",
        price: "2200.03",
        amount: "0.000527",
        executed: "100%",
        status: "closed",
      },
      {
        id: "4",
        date: "2025-02-26 10:31:51",
        market_pair: "ETH/USDT",
        side: "buy",
        type: "market",
        price: "3485.72",
        amount: "0.000527",
        executed: "100%",
        status: "closed",
      },
      {
        id: "5",
        date: "2025-02-26 00:30:57",
        market_pair: "MBC/USDT",
        side: "sell",
        type: "market",
        price: "0.0000195",
        amount: "1.7K",
        executed: "100%",
        status: "closed",
      },
    ];
  };

  // Fetch account details and orders
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const accountData = await AccountService.getAccountById(accountId);
        setAccount(accountData);

        let ordersData;
        if (tabValue === 0) {
          ordersData = await OrderService.getOpenOrdersByAccount(accountId);
        } else {
          ordersData = await OrderService.getOrderHistoryByAccount(accountId);
        }

        setOrders(ordersData || []);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
        setAccount({
          id: accountId,
          account_name: `Account ${accountId}`,
          role: "main",
          api_key: "***************",
          api_secret: "***************",
          risk_percentage: "5",
          leverage: "10",
          is_activate: true,
        });
        setOrders(getMockOrders(accountId));
      }
    };

    fetchData();
  }, [accountId, tabValue]);

  const handleChangeTab = (event, newValue) => {
    setTabValue(newValue);
  };

  // Format the table data
  const tableData = {
    columns: [
      { Header: "Date", accessor: "date", align: "left", width: "18%" },
      {
        Header: "Market pair",
        accessor: "market_pair",
        align: "left",
        width: "15%",
      },
      { Header: "Side", accessor: "side", align: "left", width: "10%" },
      { Header: "Type", accessor: "type", align: "left", width: "10%" },
      { Header: "Price", accessor: "price", align: "right", width: "12%" },
      { Header: "Amount", accessor: "amount", align: "right", width: "12%" },
      {
        Header: "Executed",
        accessor: "executed",
        align: "right",
        width: "11%",
      },
      { Header: "Status", accessor: "status", align: "center", width: "12%" },
    ],
    rows: orders.map((order) => ({
      date: (
        <MDTypography variant="caption" fontWeight="medium">
          {order.date}
        </MDTypography>
      ),
      market_pair: (
        <MDTypography variant="caption" fontWeight="medium">
          {order.market_pair}
        </MDTypography>
      ),
      side: (
        <MDTypography
          variant="caption"
          color={order.side === "buy" ? "success" : "error"}
          fontWeight="medium"
        >
          {order.side}
        </MDTypography>
      ),
      type: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {order.type}
        </MDTypography>
      ),
      price: (
        <MDTypography variant="caption" fontWeight="medium" align="right">
          ≈{order.price}
        </MDTypography>
      ),
      amount: (
        <MDTypography variant="caption" fontWeight="medium" align="right">
          {order.amount}
        </MDTypography>
      ),
      executed: (
        <MDTypography
          variant="caption"
          color="text"
          fontWeight="medium"
          align="right"
        >
          {order.executed}
        </MDTypography>
      ),
      status: (
        <MDTypography
          variant="caption"
          color={order.status === "open" ? "warning" : "text"}
          fontWeight="medium"
          align="center"
        >
          {order.status}
        </MDTypography>
      ),
    })),
  };

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
                display="flex"
                justifyContent="space-between"
              >
                <MDTypography variant="h6" color="white">
                  {account ? account.account_name : "Account Details"} - Orders
                </MDTypography>
              </MDBox>

              <MDBox p={3}>
                <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
                  <Tabs
                    value={tabValue}
                    onChange={handleChangeTab}
                    sx={{
                      "& .MuiTabs-indicator": { backgroundColor: "info.main" },
                    }}
                  >
                    <Tab
                      label="Opened"
                      sx={{
                        textTransform: "none",
                        fontSize: "1rem",
                        fontWeight: 700,
                        lineHeight: 1.625,
                        fontFamily:
                          '"Roboto", "Helvetica", "Arial", sans-serif',
                        letterSpacing: "0.0075em",
                        minWidth: "120px",
                        color: tabValue === 0 ? "#ffffff" : "text.secondary",
                        backgroundColor:
                          tabValue === 0 ? "#D3D3D3" : "transparent",
                        borderRadius: "5px 5px 0 0",
                      }}
                    />
                    <Tab
                      label="History"
                      sx={{
                        textTransform: "none",
                        fontSize: "1rem",
                        fontWeight: 700,
                        lineHeight: 1.625,
                        fontFamily:
                          '"Roboto", "Helvetica", "Arial", sans-serif',
                        letterSpacing: "0.0075em",
                        minWidth: "120px",
                        color: tabValue === 1 ? "#ffffff" : "text.secondary",
                        backgroundColor:
                          tabValue === 1 ? "#D3D3D3" : "transparent",
                        borderRadius: "5px 5px 0 0",
                        ml: 1,
                      }}
                    />
                  </Tabs>
                </Box>

                {loading ? (
                  <MDBox
                    display="flex"
                    justifyContent="center"
                    alignItems="center"
                    p={6}
                  >
                    <CircularProgress color="info" />
                  </MDBox>
                ) : (
                  <MDBox sx={{ overflowX: "auto" }}>
                    <DataTable
                      table={tableData}
                      isSorted={false}
                      entriesPerPage={{
                        defaultValue: 10,
                        entries: [5, 10, 25],
                      }}
                      showTotalEntries={true}
                      noEndBorder
                      canSearch={false}
                      sx={{
                        "& .MuiTableRow-root:nth-of-type(even)": {
                          backgroundColor: "rgba(0, 0, 0, 0.02)",
                        },
                        "& .MuiTableRow-root:hover": {
                          backgroundColor: "rgba(0, 0, 0, 0.04)",
                        },
                        "& .MuiTableHead-root": {
                          "& .MuiTableCell-head": {
                            backgroundColor: "#f8f9fa",
                            color: "text.secondary",
                            fontSize: "0.75rem",
                            fontWeight: "bold",
                            borderBottom: "1px solid #e0e0e0",
                          },
                        },
                        "& .MuiTableCell-root": {
                          padding: "12px 16px",
                        },
                      }}
                    />
                  </MDBox>
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

export default AccountDetails;
