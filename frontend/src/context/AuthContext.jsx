import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount (and whenever another tab logs in/out), check for an existing
  // token and hydrate the user from /auth/me. This is what lets a refresh
  // keep you logged in instead of bouncing you back to /login.
  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (err) {
      // Token invalid/expired — clear it so we don't loop.
      localStorage.removeItem('authToken');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();

    // Keep multiple tabs in sync: if authToken is cleared/set elsewhere,
    // re-check here too.
    const onStorage = (e) => {
      if (e.key === 'authToken') {
        loadUser();
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [loadUser]);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('authToken', response.data.access_token);
    setUser(response.data.user);
    return response.data.user;
  };

  const register = async ({ email, password, displayName }) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      display_name: displayName || undefined,
    });
    localStorage.setItem('authToken', response.data.access_token);
    setUser(response.data.user);
    return response.data.user;
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
  };

  const updateProfile = async (updates) => {
    const response = await api.put('/auth/profile', updates);
    setUser(response.data);
    return response.data;
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
    refreshUser: loadUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
