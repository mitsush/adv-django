import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ResumeUploadPage from './pages/ResumeUploadPage';

// Protected route component
const ProtectedRoute = ({ children }) => {
  // This is a simplified version. In a real app, you would check authentication status
  // and redirect to login if not authenticated
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            {/* Public routes */}
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
            
            {/* Protected routes - will be implemented as needed */}
            <Route 
              path="resumes" 
              element={
                <ProtectedRoute>
                  <div className="p-8">
                    <h1 className="text-3xl font-bold">My Resumes</h1>
                    <p className="mt-4">This page will display the user's resumes.</p>
                  </div>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="upload-resume" 
              element={
                <ProtectedRoute>
                  <ResumeUploadPage />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="jobs" 
              element={
                <div className="p-8">
                  <h1 className="text-3xl font-bold">Job Listings</h1>
                  <p className="mt-4">This page will display job listings.</p>
                </div>
              } 
            />
            
            {/* Catch-all route for 404 */}
            <Route 
              path="*" 
              element={
                <div className="flex items-center justify-center h-full p-8">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900">404</h1>
                    <p className="mt-2 text-lg text-gray-600">Page not found</p>
                    <p className="mt-4">The page you're looking for doesn't exist or has been moved.</p>
                  </div>
                </div>
              } 
            />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
