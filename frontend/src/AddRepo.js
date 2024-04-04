import React, { useEffect, useState } from "react";
import Axios from "axios";
import { Button, Form, Container, Row, Col } from "react-bootstrap";

const AddRepo = () => {
  const [projects, setProjects] = useState({});
  const [selectedRepoId, setSelectedRepoId] = useState("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await Axios.get("http://localhost:8000/api/projects");
        setProjects(response.data);
        if (Object.keys(response.data).length > 0) {
          setSelectedRepoId(Object.keys(response.data)[0]);
        }
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };

    fetchProjects();
  }, []);

  const handleAddRepo = async () => {
    try {
      const repositoryName = projects[selectedRepoId];
      const body = {
        repositoryId: selectedRepoId,
        repositoryName,
      };
      const response = await Axios.post(
        "http://localhost:8000/api/repository",
        body
      );
      console.log("Repo Added:", response.data);
    } catch (error) {
      console.error("Error adding repository:", error);
    }
  };

  return (
    <Container>
      <Row>
        <Col>
          <Form>
            <Form.Group>
              <Form.Label>Select a Repository</Form.Label>
              <Form.Control
                as="select"
                value={selectedRepoId}
                onChange={(e) => setSelectedRepoId(e.target.value)}
              >
                {Object.entries(projects).map(([id, name]) => (
                  <option key={id} value={id}>
                    {name}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
            <Button variant="primary" onClick={handleAddRepo}>
              Add Repository
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default AddRepo;
