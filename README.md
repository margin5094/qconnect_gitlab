# QConnect for GitLab

QConnect for GitLab is a comprehensive integration tool designed to streamline collaboration and communication within GitLab projects. By leveraging GitLab APIs, Django, React, MongoDB, and RabbitMQ, it facilitates the seamless retrieval and storage of GitLab user data, enabling users to generate customized queries and fetch data efficiently.

## Features

- GitLab Integration: Fetch all relevant information for specific users from their GitLab accounts.
- MongoDB Storage: Store fetched GitLab data in MongoDB for easy access and retrieval.
- Custom Query Generation: Generate queries to fetch specific data from MongoDB based on user requirements.
- Queueing with RabbitMQ: Utilize RabbitMQ for efficient task queuing and background processing.
- React Authorization: Implement React for streamlined user authorization with GitLab.

## Tech Stack

**Client:** React

**Server:** Django , RabbitMQ (CloudAMQP)

**Database:** MongoDB

## Installation

To install QConnect for GitLab (API's), follow these steps:

```bash
# Clone the repository
git clone https://github.com/yourusername/qconnect-for-gitlab.git

# Navigate to the project directory
cd qconnect-for-gitlab

# Install dependencies for the Django backend
pip install -r requirements.txt

# Configure GitLab API credentials and MongoDB connection settings in the .env files.

# Start the Django server
python manage.py runserver

# Start the RabbitMQ Consumer
python manage.py consumer
```

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file in home directory:

- `CLOUDAMQP_URL`: This variable contain the URL for CloudAMQP service, which is used for message queuing with RabbitMQ.

- `CLIENT_ID`: This variable contain the Client ID provided by GitLab for OAuth authorization.

- `CLIENT_SECRET`: This variable contain the Client Secret provided by GitLab for OAuth authorization.

- `REDIRECT_URI`: This variable contain the Redirect URI configured in GitLab OAuth application settings.

- `MONGODB_HOST`: This variable contain the hostname or IP address of MongoDB server.

- `MONGODB_USERNAME`: This variable contain the username used to authenticate with MongoDB server.

- `MONGODB_PASSWORD`: This variable contain the password used to authenticate with MongoDB server.

## Constants

Constants in project can be changed according to the needs:

- `GITLAB_API_URL`: The base URL for the GitLab API.
  - Value: `https://git.cs.dal.ca/api/v4/` (For Dalhousie University specific GitLab accounts)
  - Value: `https://gitlab.com/api/v4/` (For general GitLab accounts)
- `GITLAB_AUTH_URL`: The URL for GitLab OAuth token generation.

  - Value: `https://git.cs.dal.ca/oauth/token`
  - Value: `https://gitlab.com/oauth/token`

- `SAVE_TOKEN`: The URL where the token is saved, replaced with the appropriate server domain where backend code is deployed.
  - Value: `http://127.0.0.1:8000/api/token` (For localhost testing)
  - Value: `https://{DOMAIN NAME}/api/token` (For deployed version)

## Optimizations

In this project, several optimizations were implemented to enhance performance and efficiency:

- **Pagination Optimization**: The code has been optimized for calling the GitLab API by saving pagination information for commits and merge requests. When the API is called again, the pagination information is utilized to resume fetching from the last retrieved page. This approach significantly reduces processing time and improves overall efficiency.

## Running Tests

To run tests (Django), run the following command

```bash
 python manage.py test
```

Code coverage of 90% is acheived here. To run tests for Django and measure code coverage, execute the following command:

```bash
coverage run manage.py test
```

To generate coverage report run following command:

```bash
coverage report
```

## API Documentation

View the API documentation on [SwaggerHub](https://app.swaggerhub.com/apis/MarginPatel/qconnect_gitlab/v1#/)

## Support

For queries, email marginpatel@dal.ca (Margin Patel)

## Authors

- [Margin Patel](https://github.com/margin5094)

## Credits

I extend my sincere gratitude to Dr. Tushar Sharma and Indranil Palit for their continuous help and support throughout this project.
