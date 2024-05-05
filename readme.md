# Transparent Restaurant Backend

This REST API server is designed for managing the menu of a transparent restaurant where details about ingredient quality and meal prices are openly available. The server allows users to interact with the menu in various ways, such as retrieving meal details, listing meals based on dietary preferences, and calculating meal prices and qualities based on ingredient quality.

## Features

- **Get Meal Details**: Retrieves detailed information about specific meals, including ingredients and their options.
- **List Meals**: Provides a list of meals filtered by dietary preferences (vegetarian, vegan).
- **Calculate Quality**: Calculates the average quality score of a meal based on the quality of its ingredients.
- **Calculate Price**: Computes the total price of a meal considering ingredient quality and additional costs for lower-quality ingredients.
- **Random Meal Generator**: Returns a random meal within a specified budget with randomly assigned ingredient qualities.
- **Meal Search**: Allows searching for meals by name, supporting case-insensitive queries.

## Setup Instructions

### Prerequisites

- Python 3.7 or newer
- Access to a command line interface

### Installation

1. **Clone the Repository:**

   git clone https://github.com/BatuToy/Batuhan-Toy-otsimo-internship-task-2024.git 

2. **Navigate to the Project Directory:**

    cd TransparentRestaurantBackend


### Running the Server

To start the server, run the following command in the terminal:

    python TestServer.py


The server will be accessible on `http://localhost:8081`. You can adjust the port by modifying the `run()` function call in the `TestServer.py` file.

## API Usage

### Get Meal Details

- **Endpoint**: `GET /getMeal?id=<meal_id>`
- Retrieves detailed information about a meal.

### List Meals

- **Endpoint**: `GET /listMeals?is_vegetarian=<true/false>&is_vegan=<true/false>`
- Lists meals filtered by dietary preferences.

### Calculate Quality

- **Endpoint**: `POST /quality`
- Calculates the average quality score based on ingredient qualities.
- **Payload**:
  ```json
  {
    "meal_id": 1,
    "rice": "high",
    "chicken": "low"
  }

### Calculate Price

- **Endpoint**: `POST /price`
- Calculates the total price of a meal.
- **Payload**:
  ```json
  {
    "meal_id": 1,
    "rice": "high",
    "chicken": "low"
  }

### Random Meal Generator

- **Endpoint**: `POST /random`
- Returns a randomly selected meal within a specified budget.
- **Payload**:
  ```json
  {
    "budget": 50.00
  }

### Search for a Meal

- **Endpoint**: `GET /search?query=<name>`
- Searches for meals containing specified text.

 

### Troubleshooting 

- Ensure Python and all dependencies are correctly installed and up to date.
- If the server does not start properly, check the console for any error messages.
- Make sure the specified port is not blocked by any firewall.
 

### Contributing 

- Contributions are welcome! I mean @sercand and @utkayd :) 








