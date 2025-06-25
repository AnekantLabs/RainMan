// routes.js


// Layouts
import Dashboard from "layouts/dashboard";
import Tables from "layouts/tables";
import Billing from "layouts/billing";
import Notifications from "layouts/notifications";
import Profile from "layouts/profile";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import Accounts from "layouts/accounts";
import Logs from "layouts/logs";
import AccountDetails from "layouts/account-details";
import ProtectedRoute from "protected_routes"
// MUI icon
import Icon from "@mui/material/Icon";

// Control visibility
const disableBilling = true;
const disableNotifications = true;
const disableTables = true;

const routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <ProtectedRoute><Dashboard /></ProtectedRoute>,
  },
  {
    type: "collapse",
    name: "Tables",
    key: "tables",
    icon: <Icon fontSize="small">table_view</Icon>,
    route: "/tables",
    component: disableTables ? null : <ProtectedRoute><Tables /></ProtectedRoute>,
  },
  {
    type: "collapse",
    name: "Billing",
    key: "billing",
    icon: <Icon fontSize="small">receipt_long</Icon>,
    route: "/billing",
    component: disableBilling ? null : <ProtectedRoute><Billing /></ProtectedRoute>,
  },
  {
    type: "collapse",
    name: "Notifications",
    key: "notifications",
    icon: <Icon fontSize="small">notifications</Icon>,
    route: "/notifications",
    component: disableNotifications ? null : <ProtectedRoute><Notifications /></ProtectedRoute>,
  },
  // {
  //   type: "collapse",
  //   name: "Profile",
  //   key: "profile",
  //   icon: <Icon fontSize="small">person</Icon>,
  //   route: "/profile",
  //   component: <ProtectedRoute><Profile /></ProtectedRoute>,
  // },
  {
    type: "collapse",
    name: "Accounts",
    key: "accounts",
    icon: <Icon fontSize="small">account_circle</Icon>,
    route: "/accounts",
    component: <ProtectedRoute><Accounts /></ProtectedRoute>,
  },
  {
    type: "collapse",
    name: "Logs",
    key: "logs",
    icon: <Icon fontSize="small">history</Icon>,
    route: "/logs",
    component: <ProtectedRoute><Logs /></ProtectedRoute>,
  },
  {
    type: "collapse",
    name: "Sign In",
    key: "sign-in",
    icon: <Icon fontSize="small">login</Icon>,
    route: "/authentication/sign-in",
    component: <SignIn />,
  },
  {
    type: "collapse",
    name: "Sign Up",
    key: "sign-up",
    icon: <Icon fontSize="small">assignment</Icon>,
    route: "/authentication/sign-up",
    component: <SignUp />,
  },
  {
    type: "route",
    name: "Account Details",
    key: "account-details",
    route: "/account-details/:accountName",
    component: <ProtectedRoute><AccountDetails /></ProtectedRoute>,
    noCollapse: true,
  },
];

export default routes;
