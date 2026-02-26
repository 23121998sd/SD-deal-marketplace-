import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SocketProvider } from './context/SocketContext';
import Home from './pages/Home';
import Auth from './pages/Auth';
import BrowseServices from './pages/BrowseServices';
import ServiceDetails from './pages/ServiceDetails';
import CustomerDashboard from './pages/CustomerDashboard';
import ProviderDashboard from './pages/ProviderDashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth?mode=login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" />;
  }

  return children;
};

function AppContent() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/services" element={<BrowseServices />} />
        <Route path="/services/:id" element={<ServiceDetails />} />
        
        {/* Customer Routes */}
        <Route 
          path="/customer/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['customer']}>
              <CustomerDashboard />
            </ProtectedRoute>
          } 
        />

        {/* Provider Routes */}
        <Route 
          path="/provider/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['provider']}>
              <ProviderDashboard />
            </ProtectedRoute>
          } 
        />

        {/* Admin Routes */}
        <Route 
          path="/admin/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <div className="p-8">
                <h1 className="text-2xl font-bold">Admin Dashboard</h1>
                <p className="text-gray-600 mt-2">Manage platform, users, and transactions</p>
                <div className="mt-8 bg-white p-6 rounded-lg shadow">
                  <p className="text-gray-500">Admin dashboard coming soon with analytics, user management, and withdrawal approvals.</p>
                </div>
              </div>
            </ProtectedRoute>
          } 
        />

        {/* Chat Route */}
        <Route 
          path="/chat" 
          element={
            <ProtectedRoute>
              <div className="p-8">
                <h1 className="text-2xl font-bold">Messages</h1>
                <p className="text-gray-600 mt-2">Chat with service providers or customers</p>
                <div className="mt-8 bg-white p-6 rounded-lg shadow">
                  <p className="text-gray-500">Real-time chat interface coming soon.</p>
                </div>
              </div>
            </ProtectedRoute>
          } 
        />

        {/* Profile Route */}
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <div className="p-8">
                <h1 className="text-2xl font-bold">My Profile</h1>
                <p className="text-gray-600 mt-2">Manage your account settings</p>
                <div className="mt-8 bg-white p-6 rounded-lg shadow">
                  <p className="text-gray-500">Profile management page coming soon.</p>
                </div>
              </div>
            </ProtectedRoute>
          } 
        />

        {/* How It Works */}
        <Route 
          path="/how-it-works" 
          element={
            <div className="min-h-screen p-8">
              <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-8">How It Works</h1>
                <div className="space-y-6 bg-white p-8 rounded-lg shadow">
                  <div>
                    <h2 className="text-2xl font-bold mb-4">For Customers</h2>
                    <ol className="list-decimal list-inside space-y-2 text-gray-700">
                      <li>Browse services or search for what you need</li>
                      <li>View provider profiles and reviews</li>
                      <li>Book a service and make secure payment</li>
                      <li>Service provider accepts and completes the job</li>
                      <li>Leave a review after completion</li>
                    </ol>
                  </div>
                  <div className="mt-8">
                    <h2 className="text-2xl font-bold mb-4">For Service Providers</h2>
                    <ol className="list-decimal list-inside space-y-2 text-gray-700">
                      <li>Create your account and list your services</li>
                      <li>Receive booking requests from customers</li>
                      <li>Accept bookings and complete the service</li>
                      <li>Get paid securely to your wallet</li>
                      <li>Build your reputation with reviews</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
          } 
        />

        {/* Booking Success */}
        <Route 
          path="/booking-success" 
          element={
            <ProtectedRoute>
              <div className="min-h-screen flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold mb-2">Booking Successful!</h2>
                  <p className="text-gray-600 mb-6">Your booking has been confirmed and payment processed.</p>
                  <a href="/customer/dashboard" className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-6 py-3 rounded-lg inline-block hover:shadow-lg transition">
                    View My Bookings
                  </a>
                </div>
              </div>
            </ProtectedRoute>
          } 
        />

        {/* 404 */}
        <Route 
          path="*" 
          element={
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
                <p className="text-xl text-gray-600 mb-8">Page not found</p>
                <a href="/" className="bg-gradient-to-r from-orange-500 to-red-600 text-white px-6 py-3 rounded-lg inline-block hover:shadow-lg transition">
                  Go Home
                </a>
              </div>
            </div>
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <AppContent />
      </SocketProvider>
    </AuthProvider>
  );
}

export default App;
