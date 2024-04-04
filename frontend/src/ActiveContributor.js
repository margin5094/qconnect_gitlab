import React, { useEffect, useState } from "react";
import Axios from "axios";
import Chart from "react-apexcharts";

const ActiveContributor = ({ queryString }) => {
  const [chartOptions, setChartOptions] = useState({
    chart: {
      type: "bar",
      height: 350,
      stacked: true,
      toolbar: {
        show: true,
      },
      zoom: {
        enabled: true,
      },
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          legend: {
            position: "bottom",
            offsetX: -10,
            offsetY: 0,
          },
        },
      },
    ],
    plotOptions: {
      bar: {
        horizontal: false,
        borderRadius: 10,
      },
    },
    xaxis: {
      type: "datetime",
      categories: [],
    },
    legend: {
      position: "right",
      offsetY: 40,
    },
    fill: {
      opacity: 1,
    },
  });

  const [chartSeries, setChartSeries] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await Axios.post(
          `http://127.0.0.1:8000/api/active?${queryString}`
        );
        if (
          response.data &&
          Array.isArray(response.data) &&
          response.data.length > 0
        ) {
          const { dates, activeUsers, totalUsers } = response.data[0];

          const categories = dates.map((date) => new Date(date).toISOString());

          setChartOptions((prevOptions) => ({
            ...prevOptions,
            xaxis: { ...prevOptions.xaxis, categories },
          }));

          const seriesData = [
            { name: "Active Users", data: activeUsers },
            { name: "Total Users", data: totalUsers },
          ];

          setChartSeries(seriesData);
        }
      } catch (error) {
        console.error("Error fetching active contributors:", error);
      }
    };

    fetchData();
  }, [queryString]);

  return (
    <div id="chart">
      <Chart
        options={chartOptions}
        series={chartSeries}
        type="bar"
        height={350}
      />
    </div>
  );
};

export default ActiveContributor;
