import React from "react";
import MDButton from "components/MDButton";

/**
 * Prepares table column definitions and row data for the Accounts Table.
 *
 * Sort order:
 *  1. All "main" accounts first (by account_name)
 *  2. All "sub" accounts after (by account_name)
 *
 * @param {Array} accounts - List of account objects fetched from backend.
 * @param {Function} handleEdit - Callback to open the drawer for editing an account.
 * @returns {{columns: Array, rows: Array}}
 */
const accountsTableData = (accounts, handleEdit) => {
  const columns = [
    { Header: "Account Name", accessor: "account_name" },
    { Header: "Role", accessor: "role" },
    { Header: "API Key", accessor: "api_key" },
    { Header: "API Secret", accessor: "api_secret" },
    { Header: "Risk %", accessor: "risk_percentage" },
    { Header: "Leverage", accessor: "leverage" },
    { Header: "Active", accessor: "is_activate" },
    { Header: "Actions", accessor: "actions", align: "center" },
  ];

  // ✅ Sort accounts: main first, then subs (each alphabetically)
  const sortedAccounts = [...accounts].sort((a, b) => {
    // Prioritize "main" role first
    if (a.role === "main" && b.role !== "main") return -1;
    if (a.role !== "main" && b.role === "main") return 1;

    // If same role, sort by name alphabetically
    return (a.account_name || "").localeCompare(b.account_name || "");
  });

  const rows = sortedAccounts.map((account) => ({
    account_name: account.account_name || "—",
    role: account.role || "—",
    api_key: "••••••••",              // Masked for display
    api_secret: "••••••••",           // Masked for display
    risk_percentage:
      account.risk_percentage !== undefined && account.risk_percentage !== null
        ? `${account.risk_percentage}%`
        : "—",
    leverage:
      account.leverage !== undefined && account.leverage !== null
        ? account.leverage
        : "—",
    is_activate: account.is_activate === true ? "Yes" : "No",
    actions: (
      <MDButton
        variant="text"
        color="info"
        size="small"
        onClick={() => handleEdit(account)}
      >
        Edit
      </MDButton>
    ),
  }));

  return { columns, rows };
};

export default accountsTableData;
