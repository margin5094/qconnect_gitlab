import React, { useState } from "react";
import "./App.css";
import GitLabAuth from "./GitLabAuth";
import Graph from "./Graph";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

function App() {
  const [gitLabData, setGitLabData] = useState(null);
  return (
    <Container fluid>
      <Row>
        <Col>
          <h1 className="text-center">Login with GitLab</h1>
          <GitLabAuth
            className="d-flex align-items-center justify-content-center"
            setGitLabData={setGitLabData}
          />
          {gitLabData && <Graph gitLabData={gitLabData} />}
        </Col>
      </Row>
    </Container>
  );
}

export default App;
