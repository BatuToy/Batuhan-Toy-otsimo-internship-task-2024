import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from types import NoneType
import urllib.parse


with open('/Users/batu/Desktop/PROJECTS/TransparentRestaurantBackend/Data/dataset.json', 'r') as file:
    data = json.load(file)
    print("Data loaded successfully:", data)  # Debug: check loaded data

class MenuServer(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()      
    def send_json_error(self, status_code, message):
        self._set_headers(status_code)
        error_response = json.dumps({
            "error": True,
            "status": status_code,
            "message": message
        })
        self.wfile.write(error_response.encode('utf-8'))
    def do_GET(self):
        if self.path.startswith('/getMeal'):
            self.get_meal()
        elif self.path.startswith('/listMeals'):
            self.list_meals()
        elif self.path.startswith('/search'):
            self.handle_search()
        else:
            self.send_json_error(404, "Endpoint not found.")
    def do_POST(self):
        if self.path == '/quality':
            self.handle_quality()
        elif self.path == '/price':
            self.handle_price()
        elif self.path == '/random':
            self.handle_random_meal()
        else:
            self.send_json_error(404, 'Endpoint not found.')
    # Error handling Done    
    def get_meal(self):
        try:
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            meal_id_str = query_params.get('id', [None])[0]
            
            # Validating the meal ID
            if meal_id_str is None:
                self.send_json_error(400, "Meal ID is required.")
                return
            
            try:
                meal_id = int(meal_id_str)  
            except ValueError:
                self.send_json_error(400, "Meal ID must be an integer.")
                return
            
            # Finding the meal
            meal = next((meal for meal in data['meals'] if meal['id'] == meal_id), None)
            if not meal:
                self.send_json_error(404, 'Meal not found.')
                return

            # Constructing detailed meal information
            detailed_meal = {
                "id": meal["id"],
                "name": meal["name"],
                "ingredients": []
            }

            for ingredient in meal["ingredients"]:
                global_ingredient = next((item for item in data['ingredients'] if item['name'] == ingredient['name']), None)
                if global_ingredient:
                    detailed_ingredient = {
                        "name": ingredient['name'],
                        "groups": global_ingredient.get('groups', []),
                        "options": [
                            {
                                "name": option['name'],
                                "quality": option['quality'],
                                "price": option['price'],
                                "per_amount": option['per_amount']
                            } for option in global_ingredient.get('options', [])
                        ]
                    }
                    detailed_meal['ingredients'].append(detailed_ingredient)
                else:
                    self.send_json_error(404, f"No matching global ingredient found for: {ingredient['name']}")


            self._set_headers()
            self.wfile.write(json.dumps(detailed_meal).encode('utf-8'))

        except Exception as e:
            self.send_json_error(500, f"Internal server error: {str(e)}")
    #Error handling Done
    def list_meals(self):
        try:
            # Parse query parameters for dietary filters
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            is_vegetarian = query_components.get('is_vegetarian', ['false'])[0].lower() == 'true'
            is_vegan = query_components.get('is_vegan', ['false'])[0].lower() == 'true'

            # Prepare filtered meals based on dietary preferences
            filtered_meals = []
            for meal in data['meals']:
                meal_ingredients = meal["ingredients"]
                # Check each ingredient against the global list to determine if meal meets criteria
                ingredient_groups = [self.get_ingredient_groups(ing['name']) for ing in meal_ingredients]
                if self.meets_dietary_preference(ingredient_groups, is_vegetarian, is_vegan):
                    filtered_meals.append({
                        "id": meal["id"],
                        "name": meal["name"],
                        "ingredients": [ing['name'] for ing in meal_ingredients]
                    })

            # Sort the filtered meals by meal name alphabetically
            filtered_meals.sort(key=lambda x: x["name"])

            self._set_headers()
            self.wfile.write(json.dumps(filtered_meals).encode('utf-8'))
        
        except Exception as e:
            self.send_json_error(500, f"Internal server error: {str(e)}")
    def get_ingredient_groups(self, ingredient_name):
        for ingredient in data['ingredients']:
            if ingredient['name'] == ingredient_name:
                return ingredient.get('groups', [])
        return []
    def meets_dietary_preference(self, ingredient_groups, is_vegetarian, is_vegan):
        if is_vegan:
            return all('vegan' in groups for groups in ingredient_groups)
        elif is_vegetarian:
            return all(any(g in ['vegetarian', 'vegan'] for g in groups) for groups in ingredient_groups)
        return True  
    # Error handling Done
    def handle_quality(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data_received = json.loads(post_data.decode('utf-8'))

        meal_id = data_received.get('meal_id', None)

        if meal_id is None:
            self.send_json_error(400, "Meal ID is required.")
            return
        
        if not isinstance(meal_id, int):
            self.send_json_error(400, "Meal ID must be an integer.")
            return

        meal = next((meal for meal in data['meals'] if meal['id'] == meal_id), None)
        # Debug: check received data
        if not meal:
            self.send_json_error(404, 'Meal not found.')
            return
        # Attach the quality scores to the options
        quality_scores = {'high': 30, 'medium': 20, 'low': 10}
        total_quality = 0
        ingredient_count = 0

        for ingredient in meal['ingredients']:
            ingredient_name = ingredient['name'].lower()
            ingredient_detail = next((item for item in data['ingredients'] if item['name'].lower() == ingredient_name), None)
            # Recieve the quality data from user and check if it is in the options and get the option as a variable
            if ingredient_detail:
                selected_quality = data_received.get(ingredient_name, 'high')
                option = next((opt for opt in ingredient_detail['options'] if opt['quality'] == selected_quality), None)
                # Debug: check ingredient processing
                print(f"Processing {ingredient_name}, selected quality: {selected_quality}, option found: {option}")  # Debug
        
                if option:
                    quality_score = quality_scores.get(selected_quality, 30)  # Default to high quality
                    total_quality += quality_score
                    ingredient_count += 1
                else:
                    self.send_json_error(400, f"No option found for {ingredient_name} with quality {selected_quality}")
        if ingredient_count > 0:
            average_quality = total_quality / ingredient_count
        else:
            average_quality = 0  # Avoid the mistakes.
        
        print(f"Total quality: {total_quality}, Ingredient count: {ingredient_count}, Average quality: {average_quality}")  # Debug

        response = {"quality": average_quality}
        self._set_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    # Error handling Done
    def handle_price(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data_received = json.loads(post_data.decode('utf-8'))

            meal_id = data_received.get('meal_id', None)
            if meal_id is None:
                self.send_json_error(400, "Meal ID is required.")
                return

            # Checking if the meal_id is an instance of int directly
            if not isinstance(meal_id, int):
                self.send_json_error(400, "Meal ID must be an integer.")
                return

            meal = next((meal for meal in data['meals'] if meal['id'] == meal_id), None)
            if not meal:
                self.send_json_error(404, 'Meal not found.')
                return

            degradation_costs = {'high': 0.0, 'medium': 0.05, 'low': 0.10}
            total_cost = 0

            for ingredient in meal['ingredients']:
                ingredient_name = ingredient['name'].lower()
                ingredient_detail = next((item for item in data['ingredients'] if item['name'].lower() == ingredient_name), None)
                if ingredient_detail:
                    selected_quality = data_received.get(ingredient_name, 'high').lower()
                    option = next((opt for opt in ingredient_detail['options'] if opt['quality'].lower() == selected_quality), None)

                    if option:
                        quantity_kg = ingredient.get('quantity', 100) / 1000  # Default 100 grams if not specified
                        base_price = option['price'] * quantity_kg
                        extra_cost = degradation_costs[selected_quality]
                        total_cost += base_price + extra_cost
                    else:
                        self.send_json_error(404, f"No option found for {ingredient_name} at selected quality {selected_quality}")
                        return
                else:
                    self.send_json_error(404, f"Ingredient details not found for {ingredient_name}")
                    return

            self._set_headers()
            self.wfile.write(json.dumps({"price": round(total_cost, 2)}).encode('utf-8'))

        except Exception as e:
            self.send_json_error(500, f"Internal server error: {str(e)}")
    # Error handling Done
    def handle_random_meal(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data_received = json.loads(post_data.decode('utf-8'))
            
            budget = data_received.get('budget', None)

            # Validate the budget if it is provided
            if budget is not None:
                try:
                    budget = float(budget)  # Ensure that the budget can be converted to float
                except ValueError:
                    self.send_json_error(400, "Budget must be a valid number.")
                    return
            else:
                self.send_json_error(400, "Budget is required.")
                return

            valid_meals = []
            for meal in data['meals']:
                # Calculate the price, quality score, and ingredient details for each meal
                price, quality_score, ingredient_details = self.calculate_meal_details(meal)
                if budget is None or price <= budget:
                    valid_meals.append({
                        "id": meal["id"],
                        "name": meal["name"],
                        "price": price,
                        "quality_score": quality_score,
                        "ingredients": ingredient_details
                    })
            
            if not valid_meals:
                self.send_json_error(404, 'No meals found within the specified budget.')
                return

            # Select a random meal from valid meals
            random_meal = random.choice(valid_meals)
            self._set_headers()
            self.wfile.write(json.dumps(random_meal).encode('utf-8'))
            
        except Exception as e:
            self.send_json_error(500, f"Internal server error: {str(e)}") 
    def calculate_meal_details(self, meal):
        quality_scores = {'high': 30, 'medium': 20, 'low': 10}
        degradation_costs = {'high': 0.0, 'medium': 0.05, 'low': 0.10}
        qualities = ['high', 'medium', 'low']
        total_quality = 0
        total_cost = 0
        ingredient_details = []
        # Fetch the ingredient details from the global list for all the ingredients in the meal
        for ingredient in meal['ingredients']:
            ingredient_name = ingredient['name']
            ingredient_detail = next((item for item in data['ingredients'] if item['name'].lower() == ingredient_name.lower()), None)
            #Validations
            if ingredient_detail is None:
                print(f"Warning: No details found for ingredient {ingredient_name}")
                continue  

            selected_quality = random.choice(qualities)
            option = next((opt for opt in ingredient_detail['options'] if opt['quality'] == selected_quality), None)
            # Calculate the price and quality score for the ingredient
            if option:
                quantity_kg = ingredient.get('quantity', 100) / 1000  # Default 100 grams if not specified
                base_price = option['price'] * quantity_kg
                extra_cost = degradation_costs[selected_quality]
                total_cost += base_price + extra_cost
                total_quality += quality_scores[selected_quality]
                ingredient_details.append({
                    "name": ingredient_name,
                    "quality": selected_quality
                })
            else:
                print(f"No options found for {ingredient_name} with quality {selected_quality}")
                    
        quality_score = total_quality / len(ingredient_details) if ingredient_details else 0
        return total_cost, quality_score, ingredient_details
    def handle_search(self):
        try:
            query_components = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(query_components.query)
            search_query = query_params.get('query', [''])[0].strip().lower()  # Ensure to strip spaces and handle case

            # Validate that the search query is provided
            if not search_query:
                self.send_json_error(400, "Query parameter 'query' is required for searching.")
                return

            filtered_meals = [
                {
                    "id": meal["id"],
                    "name": meal["name"],
                    "ingredients": [ing["name"] for ing in meal["ingredients"]]
                } for meal in data['meals'] if search_query in meal["name"].lower()
            ]

            if not filtered_meals:
                self.send_json_error(404, "No meals found matching the search criteria.")
                return

            self._set_headers()
            self.wfile.write(json.dumps(filtered_meals).encode('utf-8'))

        except Exception as e:
            self.send_json_error(500, f"Internal server error: {str(e)}")
    '''
    The new endpoints are as follows:
- /getMeal: Get detailed information about a specific meal, including complete ingredient details.
- /listMeals: List all meals that meet the specified dietary preferences (vegetarian, vegan).
- /quality: Calculate the average quality score of a meal based on the quality of its ingredients.
- /price: Calculate the total price of a meal based on the quality of its ingredients.
- /random: Select a random meal that fits within a specified budget.
- /search: Search for meals based on a keyword in the meal name.
'''



def run(server_class=HTTPServer, handler_class=MenuServer, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd on {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
