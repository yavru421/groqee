# Groqee Web Assistant

Groqee is an ultra-fast, lightweight, and highly adaptable AI assistant created by John Daniel Dondlinger. This project includes a Flask-based web application and a standalone `.exe` for easy distribution.

## Features
- Chat with Groqee using a web interface.
- Upload context files to enhance responses.
- Test all functionalities with a single button.
- Toggle voice output and use voice input (if supported by the browser).
- Evolve the assistant's context dynamically.

## Running the Application

### Using the Standalone `.exe`
1. Navigate to the `dist/` folder.
2. Run `app.exe`.
3. Open your browser and go to `http://127.0.0.1:5000`.

### Using Python
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and go to `http://127.0.0.1:5000`.

## Project Structure
- `app.py`: Main Flask application.
- `static/`: Contains static files (HTML, CSS, JS, images).
- `dist/`: Contains the standalone `.exe` file.
- `README.md`: Project documentation.
- `requirements.txt`: Python dependencies.

## Preparing for Development
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application as described above.

## Contributing
Feel free to submit issues or pull requests to improve the project.

## License
This project is licensed under the MIT License.