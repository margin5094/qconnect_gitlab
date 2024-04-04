import React, { useState, useEffect } from "react";
import Axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { Card, Form, Container, Row, Col } from "react-bootstrap";
import ActivePR from "./ActivePR";
import AvgPR from "./AvgPR";
import MostActive from "./MostActive";
import ActiveContributor from "./ActiveContributor";
import AddRepo from "./AddRepo";
const customStyles = {
  card: {
    width: "18rem",

    cursor: "pointer",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    marginBottom: "1rem",
  },
  cardTitle: {
    fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontSize: "1.5rem",
    color: "#007bff",
  },
  cardText: {
    fontFamily: 'Monaco, "Lucida Console", monospace',
    backgroundColor: "#f8f9fa",
    padding: "0.5rem",
    fontSize: "2rem",
    borderRadius: "0.25rem",
  },
  datePicker: {
    marginBottom: "20px",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#ffffff",
    borderRadius: "0.25rem",
    borderColor: "#ced4da",
  },
};
const Graph = () => {
  const [dateRange, setDateRange] = useState([new Date(), new Date()]);
  const [startDate, endDate] = dateRange;
  const [activeContributors, setActiveContributors] = useState(0);
  const [repoCount, setRepoCount] = useState(null);

  const [queryString, setQueryString] = useState("");
  const [repos, setRepos] = useState([]);

  const buildQueryString = () => {
    if (!startDate || !endDate) return "";
    const formattedStartDate = startDate.toISOString().slice(0, 10);
    const formattedEndDate = endDate.toISOString().slice(0, 10);
    return (
      `startDate=${formattedStartDate}&endDate=${formattedEndDate}&` +
      repos.map((id) => `repositoryIds=${id}`).join("&")
    );
  };

  const fetchData = async () => {
    const currentQueryString = buildQueryString();
    if (!currentQueryString) return;
    setQueryString(currentQueryString);

    const urlActiveSum = `http://127.0.0.1:8000/api/active-sum?${currentQueryString}`;
    console.log(urlActiveSum);
    try {
      const responseActiveContributors = await Axios.post(urlActiveSum);
      setActiveContributors(responseActiveContributors.data.count);
      const responseAddedRepos = await Axios.get(
        `http://127.0.0.1:8000/api/added-repos`
      );

      setRepoCount(Object.keys(responseAddedRepos.data.repoIds).length);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
  };

  useEffect(() => {
    Axios.get(`http://127.0.0.1:8000/api/added-repos`)
      .then((response) => {
        console.log(Object.keys(response.data.repoIds));
        setRepos(Object.keys(response.data.repoIds));
        fetchData();
      })
      .catch((err) => console.log(err));
  }, [startDate, endDate]);

  return (
    <Container>
      <Row className="justify-content-center">
        <Col xs={12} md={6}>
          <AddRepo />
        </Col>
      </Row>
      <Row
        className="justify-content-md-center"
        style={{ marginTop: "20px", marginBottom: "20px" }}
      >
        <Col md="auto">
          <Form>
            <DatePicker
              selectsRange
              startDate={startDate}
              endDate={endDate}
              onChange={(update) => setDateRange(update)}
              dateFormat="yyyy-MM-dd"
              className="form-control"
              wrapperClassName="datePicker"
              style={customStyles.datePicker}
            />
          </Form>
        </Col>
      </Row>
      <Row className="justify-content-center">
        <Col xs={12} md={4} lg={3}>
          <Card
            bg="light"
            text="dark"
            border="primary"
            style={customStyles.card}
          >
            <Card.Body>
              <Card.Title style={customStyles.cardTitle}>
                Active Contributors
              </Card.Title>
              <Card.Text style={customStyles.cardText}>
                <pre>{JSON.stringify(activeContributors, null, 2)}</pre>
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12} md={4} lg={3}>
          <Card
            bg="light"
            text="dark"
            border="success"
            style={customStyles.card}
          >
            <Card.Body>
              <Card.Title style={customStyles.cardTitle}>
                Repositories
              </Card.Title>
              <Card.Text style={customStyles.cardText}>
                <pre>{repoCount}</pre>
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="justify-content-center">
        <Col xs={12} md={6}>
          <ActivePR queryString={queryString} />
        </Col>
        <Col xs={12} md={6}>
          <AvgPR queryString={queryString} />
        </Col>
      </Row>
      <Row className="justify-content-center">
        <Col xs={12} md={6}>
          <MostActive queryString={queryString} />
        </Col>
        <Col xs={12} md={6}>
          <ActiveContributor queryString={queryString} />
        </Col>
      </Row>
    </Container>
  );
};

export default Graph;
