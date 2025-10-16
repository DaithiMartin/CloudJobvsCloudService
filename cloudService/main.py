import os
from flask import Flask
from src.run import main

# Initialize a Flask app
app = Flask(__name__)

# This decorator defines a route; requests to "/" will be handled by this function.
@app.route("/")
def run_service():

    main()

    return 'Main function executed successfully! Check logs for more details.'

# This block starts the web server when the script is executed.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))