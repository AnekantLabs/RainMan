/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */

// @mui material components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import MDProgress from "components/MDProgress";

// Images
import logoXD from "assets/images/small-logos/logo-xd.svg";
import logoAtlassian from "assets/images/small-logos/logo-atlassian.svg";
import logoSlack from "assets/images/small-logos/logo-slack.svg";
import logoSpotify from "assets/images/small-logos/logo-spotify.svg";
import logoJira from "assets/images/small-logos/logo-jira.svg";
import logoInvesion from "assets/images/small-logos/logo-invision.svg";

export default function data() {
  const Company = ({ image, name }) => (
    <MDBox display="flex" alignItems="center" lineHeight={1}>
      <MDAvatar src={image} name={name} size="sm" />
      <MDTypography variant="button" fontWeight="medium" ml={1} lineHeight={1}>
        {name}
      </MDTypography>
    </MDBox>
  );

  return {
    columns: [
      { Header: "Account", accessor: "companies", width: "45%", align: "left" },
      { Header: "Budget", accessor: "budget", align: "center" },
      { Header: "Completion", accessor: "completion", align: "center" },
    ],

    rows: [
      {
        companies: <Company image={logoXD} name="Main Account" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            $14,000
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={60}
              color="info"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
      {
        companies: <Company image={logoAtlassian} name="Sub Account 1" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            $3,000
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={10}
              color="info"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
      {
        companies: <Company image={logoSlack} name="Sub Account 2" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Not set
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={100}
              color="success"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
      {
        companies: <Company image={logoSpotify} name="Sub Account 3" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            $20,500
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={100}
              color="success"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
      {
        companies: <Company image={logoJira} name="Sub Account 4" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            $500
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={25}
              color="info"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
      {
        companies: <Company image={logoInvesion} name="Sub Account 5" />,
        budget: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            $2,000
          </MDTypography>
        ),
        completion: (
          <MDBox width="8rem" textAlign="left">
            <MDProgress
              value={40}
              color="info"
              variant="gradient"
              label={false}
            />
          </MDBox>
        ),
      },
    ],
  };
}
