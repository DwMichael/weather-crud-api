# app/main.py
import os
from app.init_db import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv('PORT', 5000)))
