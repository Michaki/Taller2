# FastAPI Project

This is a FastAPI project. Follow the steps below to set up and run the application.

## Requirements

- Python 3.8+
- `pip` package manager

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

   Replace `main:app` with the appropriate module and app instance if different.

2. Open your browser and navigate to:

   ```
   http://127.0.0.1:8000
   ```

3. Access the interactive API documentation:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Testing

Run the tests using:

```bash
pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
