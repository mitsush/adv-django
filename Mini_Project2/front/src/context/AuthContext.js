import { jwtDecode } from 'jwt-decode';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is logged in on component mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        
        // Check if token is expired
        if (decodedToken.exp * 1000 < Date.now()) {
          handleLogout();
        } else {
          // Set user from token data
          setUser({
            id: decodedToken.user_id,
            username: decodedToken.username,
            email: decodedToken.email,
            role: decodedToken.role,
          });
        }
      } catch (err) {
        console.error('Invalid token:', err);
        handleLogout();
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.login(credentials);
      
      // Save tokens to localStorage
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      
      // Decode token to get user info
      const decodedToken = jwtDecode(response.data.access);
      
      // Set user state
      setUser({
        id: decodedToken.user_id,
        username: decodedToken.username,
        email: decodedToken.email,
        role: decodedToken.role,
      });
      
      return true;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'An error occurred during login';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      await authService.register(userData);
      return true;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'An error occurred during registration';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  const value = {
    user,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    isAuthenticated: !!user,
    isJobSeeker: user?.role === 'job_seeker',
    isRecruiter: user?.role === 'recruiter',
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 