import React, { useEffect, useState } from "react";
import Chart from "react-apexcharts";
import Axios from "axios";

const AvgPR = ({ queryString }) => {
  const [chartData, setChartData] = useState({
    options: {
      chart: {
        id: "avg-pr-chart",
        type: "area",
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
          opacityFrom: 0.7,
          opacityTo: 0.3,
        },
      },
      xaxis: {
        type: "datetime",
        categories: [],
      },
      yaxis: {
        title: {
          text: "Average Time (hours)",
        },
        labels: {
          formatter: (val) => val.toFixed(2) + "h",
        },
      },
      tooltip: {
        y: {
          formatter: (val) => val.toFixed(2) + " hours",
        },
      },
    },
    series: [
      {
        name: "Average Time to Close PRs",
        data: [],
      },
    ],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await Axios.post(
          `http://127.0.0.1:8000/api/avg-time-close?${queryString}`
        );
        const { dates, times } = response.data;
        const timesInHours = times;

        setChartData({
          options: {
            ...chartData.options,
            xaxis: {
              ...chartData.options.xaxis,
              categories: dates.map((date) => new Date(date).toISOString()),
            },
          },
          series: [{ name: "Average Time to Close PRs", data: timesInHours }],
        });
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

export default AvgPR;
