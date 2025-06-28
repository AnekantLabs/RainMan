import React from "react";
import MDButton from "components/MDButton";
import MDBox from "components/MDBox";

/**
 * Prepares table column definitions and row data for the Accounts Table.
 *
 * Sort order:
 *  1. All "main" accounts first (by account_name)
 *  2. All "sub" accounts after (by account_name)
 *
 * @param {Array} accounts - List of account objects fetched from backend.
 * @param {Function} handleEdit - Callback to open the drawer for editing an account.
 * @param {Function} handleDelete - Callback to delete an account.
 * @returns {{columns: Array, rows: Array}}
 */
const accountsTableData = (accounts, handleEdit, handleDelete) => {
  const columns = [
    { Header: "Account Name", accessor: "account_name" },
    { Header: "Role", accessor: "role" },
    { Header: "API Key", accessor: "api_key" },
    { Header: "API Secret", accessor: "api_secret" },
    { Header: "Active", accessor: "is_activate", align: "center" },
    { Header: "Actions", accessor: "actions", align: "center" },
  ];

  const sortedAccounts = [...accounts].sort((a, b) => {
    if (a.role === "main" && b.role !== "main") return -1;
    if (a.role !== "main" && b.role === "main") return 1;
    return (a.account_name || "").localeCompare(b.account_name || "");
  });

  const rows = sortedAccounts.map((account) => ({
    account_name: account.account_name || "—",
    role: account.role || "—",
    api_key: "••••••••",
    api_secret: "••••••••",
    is_activate: account.is_activate === true ? "Yes" : "No",
    actions: (
      <MDBox display="flex" gap={1}>
        <MDButton
          variant="text"
          color="info"
          size="small"
          onClick={() => handleEdit(account)}
          sx={{
            minWidth: "60px",
            padding: "4px 8px",
            fontSize: "0.875rem",
          }}
        >
          Edit
        </MDButton>
        <MDButton
          variant="text"
          color="error"
          size="small"
          onClick={() => handleDelete(account.id)}
          sx={{
            minWidth: "60px",
            padding: "4px 8px",
            fontSize: "0.875rem",
            "&:hover": {
              backgroundColor: "rgba(244, 67, 54, 0.1)",
            },
          }}
        >
          Delete
        </MDButton>
      </MDBox>
    ),
  }));

  return { columns, rows };
};

export default accountsTableData;