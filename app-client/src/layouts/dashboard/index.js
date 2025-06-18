// @mui material components
import Grid from "@mui/material/Grid";
import CircularProgress from "@mui/material/CircularProgress";

// Rainman React components
import MDBox from "components/MDBox";
import { useState, useEffect } from "react";
import axios from "axios";

// Rainman React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";

// Dashboard components
import Projects from "layouts/dashboard/components/Projects";
import LogsOverview from "layouts/dashboard/components/LogsOverview";

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTrades: 0,
    totalProfit: 0,
    totalLoss: 0,
    drawdown: 0,
  });

  const [trades, setTrades] = useState([]);
  const [todayClosedTrades, setTodayClosedTrades] = useState(0);
  const [totalPnl, setTotalPnl] = useState(0);

  const [dailyChart, setDailyChart] = useState({ labels: [], datasets: [] });
  const [categoryBar, setCategoryBar] = useState({ labels: [], datasets: [] });
  const [accountBarData, setAccountBarData] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    const fetchAndProcessTrades = () => {
      axios.get("http://localhost:8000/api/v1/trades")
        .then((res) => {
          const data = res.data;
          setTrades(data);
          processStats(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to fetch trades:", err);
          setLoading(false);
        });
    };

    fetchAndProcessTrades();
    const interval = setInterval(fetchAndProcessTrades, 60000);
    return () => clearInterval(interval);
  }, []);

  const processStats = (data) => {
    const closedTradesCount = data.filter(
      (t) => t.closed_pnl !== null && t.closed_pnl !== undefined && t.closed_pnl !== 0
    ).length;

    let totalProfit = 0;
    let totalLoss = 0;
    let todayClosedCount = 0;
    let allClosedPnl = 0;

    const now = new Date();
    const todayStr = now.toLocaleDateString();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const dayMap = {};
    const categoryMap = {};
    const accountMap = {};

    const intradayPnlMap = {};
    let cumulativePnl = 0;

    data.forEach((trade) => {
      const pnl = trade.closed_pnl;
      const createdDate = new Date(trade.created_time);
      const tradeDateStr = createdDate.toLocaleDateString();

      const isToday =
        createdDate.getDate() === now.getDate() &&
        createdDate.getMonth() === now.getMonth() &&
        createdDate.getFullYear() === now.getFullYear();

      if (pnl !== null && pnl !== undefined && pnl !== 0) {
        allClosedPnl += pnl;

        if (tradeDateStr === todayStr) {
          todayClosedCount++;
        }

        if (pnl > 0) totalProfit += pnl;
        else totalLoss += Math.abs(pnl);
      }

      dayMap[tradeDateStr] = (dayMap[tradeDateStr] || 0) + (pnl || 0);

      const cat = trade.category || "Uncategorized";
      categoryMap[cat] = (categoryMap[cat] || 0) + (pnl || 0);

      if (createdDate.getMonth() === currentMonth && createdDate.getFullYear() === currentYear) {
        const account = trade.account_name || "Unknown";
        accountMap[account] = (accountMap[account] || 0) + (pnl || 0);
      }

      // Intraday PnL for today
      if (pnl !== null && pnl !== undefined && pnl !== 0 && isToday) {
        const timeStr = createdDate.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
        cumulativePnl += pnl;
        intradayPnlMap[timeStr] = cumulativePnl;
      }
    });

    // Build Intraday PnL Chart
    const sortedTimes = Object.keys(intradayPnlMap).sort(
      (a, b) => new Date(`1970-01-01T${a}`) - new Date(`1970-01-01T${b}`)
    );
    const sortedPnls = sortedTimes.map((t) => intradayPnlMap[t]);
    setDailyChart({
      labels: sortedTimes,
      datasets: [{ label: "Intraday PnL", data: sortedPnls }],
    });

    // PnL by category
    const barLabels = Object.keys(categoryMap);
    const barData = Object.values(categoryMap);
    setCategoryBar({
      labels: barLabels,
      datasets: [{ label: "PnL by Category", data: barData }],
    });

    // Monthly PnL by account
    const accountLabels = Object.keys(accountMap);
    const accountValues = Object.values(accountMap);
    setAccountBarData({
      labels: accountLabels,
      datasets: [{
        label: "Monthly PnL by Account",
        backgroundColor: accountValues.map((v) =>
          v >= 0 ? "rgba(76, 175, 80, 0.8)" : "rgba(244, 67, 54, 0.8)"
        ),
        data: accountValues,
      }],
    });

    // Drawdown
    let runningTotal = 0, peak = 0, maxDD = 0;
    sortedPnls.forEach(val => {
      runningTotal = val;
      peak = Math.max(peak, runningTotal);
      const dd = ((peak - runningTotal) / peak) * 100;
      maxDD = Math.max(maxDD, dd);
    });

    setStats({
      totalTrades: closedTradesCount,
      totalProfit: totalProfit.toFixed(2),
      totalLoss: totalLoss.toFixed(2),
      drawdown: maxDD.toFixed(2),
    });

    setTodayClosedTrades(todayClosedCount);
    setTotalPnl(allClosedPnl.toFixed(2));
  };

  if (loading) {
    return (
      <DashboardLayout>
        <DashboardNavbar />
        <MDBox p={4} textAlign="center">
          <CircularProgress />
        </MDBox>
        <Footer />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="info"
                icon="event"
                title="Today's Closed Trades"
                count={todayClosedTrades}
                percentage={{
                  color: "success",
                  amount: "",
                  label: "Trades closed today",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="leaderboard"
                title="Total Loss"
                count={`$${stats.totalLoss}`}
                percentage={{
                  color: "error",
                  amount: "",
                  label: "Closed Losses",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="store"
                title="Profit"
                count={`$${stats.totalProfit}`}
                percentage={{
                  color: "success",
                  amount: "",
                  label: "Closed Profits",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={2.9}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="paid"
                title="Total PnL"
                count={`$${totalPnl}`}
                percentage={{
                  color: totalPnl >= 0 ? "success" : "error",
                  amount: "",
                  label: "Across all accounts",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>

        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="success"
                  title="Intraday PnL"
                  description="Cumulative PnL today by time"
                  date="Updated just now"
                  chart={dailyChart}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="dark"
                  title="Current Month PnL by Account"
                  description="Histogram of account performance"
                  date="Updated just now"
                  chart={accountBarData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="info"
                  title="PnL by Category"
                  description="Category-wise distribution"
                  date="Updated live"
                  chart={categoryBar}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>

        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={8}>
              <Projects />
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <LogsOverview />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
