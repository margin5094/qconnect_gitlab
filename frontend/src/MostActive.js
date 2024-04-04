import React, { useEffect, useState } from "react";
import Axios from "axios";
import Card from "react-bootstrap/Card";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const MostActive = ({ queryString }) => {
  const [mostActiveUsers, setMostActiveUsers] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await Axios.post(
          `http://127.0.0.1:8000/api/most-active?${queryString}`
        );
        console.log(response);
        setMostActiveUsers(response.data);
      } catch (error) {
        console.error("Error fetching most active users:", error);
      }
    };

    fetchData();
  }, [queryString]);

  return (
    <Container className="p-3" style={{ maxWidth: "600px" }}>
      {"Most Active Contributors"}
      {mostActiveUsers.map((user, index) => (
        <Card
          key={index}
          className="mb-2 shadow-sm"
          style={{
            fontSize: "1rem",
            backgroundColor: "#f9f9f9",
            padding: "10px",
          }}
        >
          <Row className="align-items-center justify-content-between m-0">
            {" "}
            {}
            <Col xs="auto" style={{ color: "#0056b3" }}>
              {user.name}
            </Col>{" "}
            {}
            <Col xs="auto" style={{ color: "#28a745" }}>
              {user.email}
            </Col>{" "}
            {}
            <Col xs="auto" style={{ color: "#dc3545" }}>
              {user.commits} Commits
            </Col>{" "}
            {}
          </Row>
        </Card>
      ))}
    </Container>
  );
};

export default MostActive;
