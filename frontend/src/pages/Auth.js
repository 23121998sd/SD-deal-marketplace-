import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft } from 'lucide-react';

const Auth = () => {
  const [searchParams] = useSearchParams();
  const initialMode = searchParams.get('mode') || 'login';
  const initialRole = searchParams.get('role') || 'customer';
  
  const [mode, setMode] = useState(initialMode);
  const [role, setRole] = useState(initialRole);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let userData;
      if (mode === 'login') {
        userData = await login(formData.email, formData.password);
      } else {
        userData = await register(formData.email, formData.password, formData.full_name, formData.phone, role);
      }
      
      // Redirect based on user role
      const userRole = userData?.role || role;
      if (userRole === 'provider') {
        navigate('/provider/dashboard');
      } else if (userRole === 'customer') {
        navigate('/customer/dashboard');
      } else if (userRole === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <Link to="/" className="flex items-center text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Home
        </Link>
        
        <div className="bg-white rounded-2xl shadow-xl p-8" data-testid="auth-form">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              {mode === 'login' ? 'Welcome Back' : 'Get Started'}
            </h2>
            <p className="text-gray-600 mt-2">
              {mode === 'login' ? 'Sign in to your account' : 'Create your account'}
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg" data-testid="auth-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {mode === 'register' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    data-testid="fullname-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    data-testid="phone-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    I want to
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      type="button"
                      onClick={() => setRole('customer')}
                      className={`py-3 px-4 rounded-lg border-2 transition ${
                        role === 'customer'
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                      data-testid="role-customer-button"
                    >
                      Find Services
                    </button>
                    <button
                      type="button"
                      onClick={() => setRole('provider')}
                      className={`py-3 px-4 rounded-lg border-2 transition ${
                        role === 'provider'
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                      data-testid="role-provider-button"
                    >
                      Offer Services
                    </button>
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                data-testid="email-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                data-testid="password-input"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
              data-testid="auth-submit-button"
            >
              {loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
              {' '}
              <button
                onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                className="text-blue-600 hover:text-blue-700 font-semibold"
                data-testid="toggle-auth-mode-button"
              >
                {mode === 'login' ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
