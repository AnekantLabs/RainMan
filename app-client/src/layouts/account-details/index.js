import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Grid, Card, CircularProgress } from "@mui/material";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DataTable from "examples/Tables/DataTable";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import OrderService from "services/orderService";

function AccountDetails() {
  const { accountName } = useParams();
  const navigate = useNavigate();
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accountName) {
      console.warn("Missing accountName in URL, redirecting...");
      navigate("/accounts");
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        const tradeData = await OrderService.getTradesByAccountName(accountName);
        setTrades(
          (tradeData || []).sort(
            (a, b) => new Date(b.created_time) - new Date(a.created_time)
          )
        );
      } catch (error) {
        console.error("Error fetching trades:", error);
        setTrades([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [accountName, navigate]);

  const tableData = {
    columns: [
      { Header: "Date", accessor: "date", align: "left", width: "18%" },
      { Header: "Market pair", accessor: "market_pair", align: "left", width: "15%" },
      { Header: "Side", accessor: "side", align: "left", width: "10%" },
      { Header: "Type", accessor: "type", align: "left", width: "10%" },
      { Header: "Price", accessor: "price", align: "right", width: "12%" },
      { Header: "Amount", accessor: "amount", align: "right", width: "12%" },
      { Header: "Executed", accessor: "executed", align: "right", width: "11%" },
      { Header: "Status", accessor: "status", align: "center", width: "12%" },
    ],
    rows: trades.map((trade) => ({
      date: (
        <MDTypography variant="caption" fontWeight="medium">
          {trade.created_time ? new Date(trade.created_time).toLocaleString() : "N/A"}
        </MDTypography>
      ),
      market_pair: (
        <MDTypography variant="caption" fontWeight="medium">
          {trade.symbol || "—"}
        </MDTypography>
      ),
      side: (
        <MDTypography
          variant="caption"
          color={
            trade.side?.toLowerCase() === "buy"
              ? "success"
              : trade.side?.toLowerCase() === "sell"
              ? "error"
              : "text"
          }
          fontWeight="medium"
        >
          {trade.side || "—"}
        </MDTypography>
      ),
      type: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {trade.order_type || "—"}
        </MDTypography>
      ),
      price: (
        <MDTypography variant="caption" fontWeight="medium" align="right">
          ≈{trade.price ?? "—"}
        </MDTypography>
      ),
      amount: (
        <MDTypography variant="caption" fontWeight="medium" align="right">
          {trade.qty ?? "—"}
        </MDTypography>
      ),
      executed: (
        <MDTypography variant="caption" fontWeight="medium" align="right">
          {trade.cum_exec_qty ?? "—"}/{trade.qty ?? "—"}
        </MDTypography>
      ),
      status: (
        <MDTypography
          variant="caption"
          color={trade.status === "open" ? "warning" : "text"}
          fontWeight="medium"
          align="center"
        >
          {trade.status || "—"}
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
                  {accountName} - Trades
                </MDTypography>
              </MDBox>

              <MDBox p={3}>
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
                      entriesPerPage={{ defaultValue: 10, entries: [5, 10, 25] }}
                      showTotalEntries={true}
                      noEndBorder
                      canSearch={false}
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
