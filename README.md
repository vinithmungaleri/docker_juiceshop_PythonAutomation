## Pre-requisites
Please ensure you have the following set up on your system:

- **Docker:** Install Docker on your system to run the Juice Shop application in a container.
Download from the [official website](https://www.docker.com/).

### Setting up Juice Shop Application
We will be using JuiceShop application during our discussion, please ensure that you have
JuiceShop application running on your system in a docker container.

Run the following to download the image and start the container:
`docker run -d -p 3000:3000 bkimminich/juice-shop`

Open your web browser and navigate to http://localhost:3000 to ensure the Juice Shop
application is up and running.

Please manually register a user in JuiceShop application. Update your credentials in config.json.

**Scenarios covered:**
Scenario 1: Manually create a new user and add their credentials to the config.json file. Then create a
login script in the setup fixture to login every time a test runs.

Scenario 2: Create a UI test that navigates to My Payments options from homescreen(UI tests) and
add card details

Scenario 3: Create an API test that adds a unique card details



Tech stack used: Python, Selenium, API, Pytest.
