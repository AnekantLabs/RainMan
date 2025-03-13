
import Button from "@mui/material/Button";
import MDBadge from "components/MDBadge";

export default function accountsTableData(rows, handleOpenDrawer) {
    return {
        columns: [
            { Header: "Account Name", accessor: "account_name", align: "left" },
            { Header: "Role", accessor: "role", align: "left" },
            { Header: "API Key", accessor: "api_key", align: "left" },
            { Header: "API Secret", accessor: "api_secret", align: "left" },
            { Header: "Risk %", accessor: "risk_percentage", align: "center" },
            { Header: "Leverage", accessor: "leverage", align: "center" },
            { Header: "Status", accessor: "is_activate", align: "center" },
            { Header: "Action", accessor: "action", align: "center" },
        ],
        rows: rows.map((account) => ({
            ...account,
            is_activate: account.is_activate ? (
                <MDBadge badgeContent="Active" color="success" variant="gradient" size="sm" />
            ) : (
                <MDBadge badgeContent="Inactive" color="dark" variant="gradient" size="sm" />
            ),
            action: (
                <Button onClick={() => handleOpenDrawer(account)}>Edit</Button>
            ),
        })),
    };
}