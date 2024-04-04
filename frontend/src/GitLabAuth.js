import React, { useEffect, useState } from "react";
import axios from "axios";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGitlab } from "@fortawesome/free-brands-svg-icons";
import { faSync } from "@fortawesome/free-solid-svg-icons";
import { Card, Button, Container, Spinner } from "react-bootstrap";

const GitLabAuth = ({ setGitLabData }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncLoading, setSyncLoading] = useState(false);

  useEffect(() => {
    const storedToken = sessionStorage.getItem("access_token");
    if (storedToken) {
      setData("ok");
      setLoading(false);
      setGitLabData("ok");
      return;
    }
    const handleCallback = async () => {
      const code = new URLSearchParams(window.location.search).get("code");
      if (code) {
        try {
          console.log(code);
          const response = await axios.post(
            "http://127.0.0.1:8000/api/gitlab-auth",
            {
              code,
            }
          );
          setData("ok");
          setGitLabData("ok");
          sessionStorage.setItem("access_token", "ok");

          window.history.pushState({}, document.title, "/");
        } catch (error) {
          console.error("Error getting access token:", error);
        }
      }
      setLoading(false);
    };

    handleCallback();
  }, []);

  const handleLogin = () => {
    window.location.href = `https://git.cs.dal.ca/oauth/authorize?client_id=d105231a78c0ac4bb72663033bac467f917ea8b84c32784a5ad73726b4c12631&redirect_uri=http://localhost:3000/callback&response_type=code&scope=read_user%20read_repository%20read_api`;
  };

  const handleSynchronize = async () => {
    setSyncLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/api/synchronize");

      console.log("Synchronization successful");
    } catch (error) {
      console.error("Synchronization failed:", error);
    }
    setSyncLoading(false);
  };
  return (
    <Container className="d-flex justify-content-center align-items-center">
      <Card style={{ width: "250px" }}>
        <Card.Header className="text-center">Connect with GitLab</Card.Header>
        <Card.Body>
          {loading ? (
            <p>Loading...</p>
          ) : data ? (
            <div className="d-flex align-items-center justify-content-between">
              <FontAwesomeIcon
                icon={faGitlab}
                size="2x"
                style={{ color: "orange" }}
              />
              {syncLoading ? (
                <Spinner animation="border" />
              ) : (
                <Button variant="success" onClick={handleSynchronize}>
                  <FontAwesomeIcon icon={faSync} size="lg" /> Synchronize
                </Button>
              )}
            </div>
          ) : (
            <div className="d-flex align-items-center justify-content-center">
              <FontAwesomeIcon
                icon={faGitlab}
                size="2x"
                style={{ marginRight: "7px", color: "orange" }}
              />
              <Button variant="primary" onClick={handleLogin} className="ml-2">
                Connect via GitLab
              </Button>
            </div>
          )}
        </Card.Body>
        <Card.Footer
          className="text-center"
          style={{ color: data ? "green" : "" }}
        >
          {data ? "Connected" : "Not Connected"}
        </Card.Footer>
      </Card>
    </Container>
  );
};

export default GitLabAuth;
