import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API_URL}/auth/login`, { email, password });
    const { access_token, user: userData } = response.data;
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('token', access_token);
    return userData;
  };

  const register = async (email, password, full_name, phone, role) => {
    const response = await axios.post(`${API_URL}/auth/register`, {
      email,
      password,
      full_name,
      phone,
      role
    });
    const { access_token, user: userData } = response.data;
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('token', access_token);
    return userData;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const updateProfile = async (updates) => {
    const response = await axios.put(`${API_URL}/auth/profile`, updates, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setUser(response.data);
    return response.data;
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
