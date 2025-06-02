# Patient Document Scanner

This repository contains a web application for scanning and analyzing patient documents using OpenAI's API. The application includes a frontend built with Next.js and a backend powered by Flask.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **pip** (Python package manager)
- **Cargo** (Rust package manager, required for Tauri)

## Cloning the Repository

1. Clone the repository:

   ```bash
   git clone https://github.com/RiyadKT/rainpath
   cd new-scanner
   ```

2. Install dependencies for the frontend:

   ```bash
   npm install
   ```

3. Install dependencies for the backend:

   ```bash
   pip install -r api/requirements.txt
   ```

## Setting Up API Keys

The application requires API keys for OpenAI and ImgBB. These keys are not included in the repository and must be added manually:

1. **OpenAI API Key**:
   - Create a file named `key.txt` in the `api/` directory.
   - Add your OpenAI API key to this file.

2. **ImgBB API Key**:
   - Create a file named `image_api.txt` in the `api/` directory.
   - Add your ImgBB API key to this file.

## Running the Application

### Backend

1. Navigate to the `api/` directory:

   ```bash
   cd api
   ```

2. Start the Flask server:

   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5006`.

### Frontend

1. Navigate to the root directory:

   ```bash
   cd ..
   ```

2. Start the Next.js development server:

   ```bash
   npm run dev
   ```

   The frontend will run on `http://localhost:3000`.

### Tauri Application

1. Navigate to the `src-tauri/` directory:

   ```bash
   cd src-tauri
   ```

2. Build and run the Tauri application:

   ```bash
   cargo tauri dev
   ```

## Notes

- Ensure the backend is running before using the frontend or Tauri application.
- Temporary files are stored in the `api/temp_files/` directory and are automatically cleaned up.

## Troubleshooting

If you encounter issues, check the following:

- Ensure API keys are correctly configured.
- Verify that all dependencies are installed.
- Check the console logs for error messages.

## License

This project is licensed under the MIT License.