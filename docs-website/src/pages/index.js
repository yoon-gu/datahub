import React, { useEffect } from "react";
import { Redirect } from "@docusaurus/router";

export default function Home() {
  useEffect(() => {
    window.location.href = "/datahub/docs";
  }, []);

  return <Redirect to="/datahub/docs" />;
}
