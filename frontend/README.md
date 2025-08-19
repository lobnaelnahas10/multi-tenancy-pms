# Project Management System - Frontend

This is the frontend for the Project Management System, built with React and Material-UI.

## Prerequisites

- Node.js 16 or higher
- npm 8 or higher
- Backend service (see backend/README.md)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PMS/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   Create a `.env` file in the `frontend` directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000/api
   ```

## Running the Application

1. **Start the development server**
   ```bash
   npm start
   ```
   The application will be available at `http://localhost:3000`

2. **Login**
   - Use the login page to sign in with your credentials
   - Or register a new account if you don't have one by navigating to '/register'

## Project Structure

```
frontend/
├── public/           # Static files
└── src/
    ├── api/          # API service functions
    ├── components/   # Reusable UI components
    ├── pages/        # Page components
    ├── App.js        # Main application component
    └── index.js      # Application entry point
```

## Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Create production build
- `npm run eject` - Eject from Create React App (not recommended)

## Development

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Keep components small and focused
- Write tests for new features

## Deployment

To create a production build:

```bash
npm run build
```

This will create an optimized production build in the `build` folder that can be served by any static file server or CDN.

## Backend Integration

The frontend communicates with the backend API. Make sure the backend service is running and properly configured (see backend/README.md).

## License

[Your License Here]

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
