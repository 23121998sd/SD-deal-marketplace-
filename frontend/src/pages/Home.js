import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCategories, getServices } from '../api/api';
import { useAuth } from '../context/AuthContext';
import { Search, MapPin, Star, ArrowRight, CheckCircle, Shield, Clock, Users } from 'lucide-react';

const Home = () => {
  const [categories, setCategories] = useState([]);
  const [featuredServices, setFeaturedServices] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesRes, servicesRes] = await Promise.all([
        getCategories(),
        getServices({ sort_by: 'rating' })
      ]);
      setCategories(categoriesRes.data);
      setFeaturedServices(servicesRes.data.slice(0, 6));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/services?search=${searchQuery}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50" data-testid="main-navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-2xl">SD</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-600">SD DEAL</span>
                <span className="text-xs text-gray-500 -mt-1">Service Marketplace</span>
              </div>
            </Link>
            
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/services" className="text-gray-700 hover:text-blue-600 transition">Browse Services</Link>
              <Link to="/how-it-works" className="text-gray-700 hover:text-blue-600 transition">How It Works</Link>
              {user && user.role === 'provider' && (
                <Link to="/provider/dashboard" className="text-gray-700 hover:text-blue-600 transition">Dashboard</Link>
              )}
              {user && user.role === 'customer' && (
                <Link to="/customer/dashboard" className="text-gray-700 hover:text-blue-600 transition">My Bookings</Link>
              )}
              {user && user.role === 'admin' && (
                <Link to="/admin/dashboard" className="text-gray-700 hover:text-blue-600 transition">Admin</Link>
              )}
            </div>

            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <Link to="/chat" className="text-gray-700 hover:text-blue-600">
                    <Users className="w-5 h-5" />
                  </Link>
                  <Link to="/profile" className="flex items-center space-x-2 text-gray-700 hover:text-blue-600">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">
                      {user.full_name.charAt(0)}
                    </div>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/auth?mode=login" data-testid="login-button" className="text-gray-700 hover:text-blue-600 transition">Login</Link>
                  <Link to="/auth?mode=register" data-testid="register-button" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">Get Started</Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8" data-testid="hero-section">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Find the Best <span className="text-blue-600">Local Services</span>
            <br />Near You
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Connect with trusted professionals for all your service needs. Book instantly, pay securely, and get the job done.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-12" data-testid="search-form">
            <div className="flex items-center bg-white rounded-full shadow-lg p-2">
              <Search className="w-6 h-6 text-gray-400 ml-4" />
              <input
                type="text"
                placeholder="What service are you looking for?"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-3 outline-none"
                data-testid="search-input"
              />
              <button
                type="submit"
                className="bg-blue-600 text-white px-8 py-3 rounded-full hover:bg-blue-700 transition"
                data-testid="search-submit-button"
              >
                Search
              </button>
            </div>
          </form>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div>
              <div className="text-3xl font-bold text-blue-600">10K+</div>
              <div className="text-gray-600">Services</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">5K+</div>
              <div className="text-gray-600">Providers</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">50K+</div>
              <div className="text-gray-600">Bookings</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">4.8★</div>
              <div className="text-gray-600">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50" data-testid="categories-section">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Popular Categories</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {categories.map(category => (
              <Link
                key={category.id}
                to={`/services?category=${category.id}`}
                className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition text-center group"
                data-testid={`category-${category.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <div className="text-4xl mb-3">{category.icon || '🔧'}</div>
                <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition">
                  {category.name}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Services */}
      <section className="py-16 px-4 sm:px-6 lg:px-8" data-testid="featured-services-section">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Top Rated Services</h2>
            <Link to="/services" className="text-blue-600 hover:text-blue-700 flex items-center space-x-2">
              <span>View All</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredServices.map(service => (
              <Link
                key={service.id}
                to={`/services/${service.id}`}
                className="bg-white rounded-xl shadow-sm hover:shadow-lg transition overflow-hidden group"
                data-testid={`service-card-${service.id}`}
              >
                <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                  <div className="text-6xl">{service.category?.icon || '🔧'}</div>
                </div>
                <div className="p-6">
                  <h3 className="font-bold text-lg text-gray-900 mb-2 group-hover:text-blue-600 transition">
                    {service.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{service.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-semibold">{service.rating.toFixed(1)}</span>
                      <span className="text-sm text-gray-500">({service.total_bookings})</span>
                    </div>
                    <div className="text-lg font-bold text-blue-600">${service.price}</div>
                  </div>
                  {service.provider && (
                    <div className="mt-4 pt-4 border-t flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm">
                        {service.provider.full_name.charAt(0)}
                      </div>
                      <div className="text-sm text-gray-600">{service.provider.full_name}</div>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50" data-testid="features-section">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">Why Choose ServiceMarket?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Verified Providers</h3>
              <p className="text-gray-600">All service providers are verified and background checked</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Secure Payments</h3>
              <p className="text-gray-600">Payments are held securely until service completion</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Instant Booking</h3>
              <p className="text-gray-600">Book services instantly with real-time availability</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Quality Reviews</h3>
              <p className="text-gray-600">Read authentic reviews from verified customers</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-600" data-testid="cta-section">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of satisfied customers and providers on ServiceMarket
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/auth?mode=register&role=customer"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition"
              data-testid="cta-find-services-button"
            >
              Find Services
            </Link>
            <Link
              to="/auth?mode=register&role=provider"
              className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition"
              data-testid="cta-become-provider-button"
            >
              Become a Provider
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-4">ServiceMarket</h3>
              <p className="text-gray-400">Connecting customers with trusted local service providers.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Customers</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/services" className="hover:text-white">Browse Services</Link></li>
                <li><Link to="/how-it-works" className="hover:text-white">How It Works</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Providers</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/auth?mode=register&role=provider" className="hover:text-white">Become a Provider</Link></li>
                <li><Link to="/provider/dashboard" className="hover:text-white">Provider Dashboard</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/about" className="hover:text-white">About Us</Link></li>
                <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 ServiceMarket. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
