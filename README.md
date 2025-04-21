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
   python -m uvicorn app.main:app --reload
   ```

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

## Environment Variables

This project uses environment variables for configuration. Create a `.env` file in the root directory and add your environment variables there. For example:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
```

## Database Setup

1. Install Docker and Docker Compose if you haven't already.
2. Run the following command to start the elasticsearch container:

   ```bash
   docker-compose up -d
   ```

Note: this has to be run in the root directory of the project.

## Database Migrations

It needs to run migrations to set up the database seed data and index, to run the migrations, use the following command:

```bash
python manage.py migrate
```

You need to have the `manage.py` file in the root directory of the project. This file is used to manage database migrations and other tasks.

## License

This project is licensed under the [MIT License](LICENSE).
