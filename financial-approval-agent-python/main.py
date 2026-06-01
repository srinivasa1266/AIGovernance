# main.py — project entrypoint
# Run with: python main.py
# Or via Docker: CMD ["python", "main.py"]

from src.server import app
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
