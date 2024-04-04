import React, { useEffect, useState } from "react";
import Chart from "react-apexcharts";
import Axios from "axios";

const ActivePR = ({ queryString }) => {
  const [chartData, setChartData] = useState({
    options: {
      chart: {
        id: "active-pr-chart",
        type: "area",
        stacked: false,
        zoom: {
          enabled: true,
        },
        toolbar: {
          autoSelected: "zoom",
        },
      },
      dataLabels: {
        enabled: false,
      },
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          inverseColors: false,
          opacityFrom: 0.5,
          opacityTo: 0.1,
          stops: [0, 90, 100],
        },
      },
      legend: {
        position: "top",
        horizontalAlign: "left",
      },
      xaxis: {
        type: "datetime",
        categories: [],
      },
    },
    series: [
      {
        name: "Active",
        data: [],
      },
      {
        name: "Newly Created",
        data: [],
      },
    ],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await Axios.post(
          `http://127.0.0.1:8000/api/active-new?${queryString}`
        );
        const { dates, active, newly_created } = response.data;

        if (dates && active && newly_created) {
          setChartData((prevChartData) => ({
            ...prevChartData,
            options: {
              ...prevChartData.options,
              xaxis: {
                ...prevChartData.options.xaxis,
                categories: dates.map((date) => new Date(date).toISOString()),
              },
            },
            series: [
              { name: "Active", data: active },
              { name: "Newly Created", data: newly_created },
            ],
          }));
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [queryString]);

  return (
    <div>
      <Chart
        options={chartData.options}
        series={chartData.series}
        type="area"
        height="350"
      />
    </div>
  );
};

export default ActivePR;
