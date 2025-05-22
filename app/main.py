# app/main.py
import os
from app.init_db import create_dash_app

app = create_dash_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv('PORT', 5000)))
