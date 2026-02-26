import React, { useState, useEffect } from 'react';
import { getMyServices, getBookings, getWallet, createService, updateService } from '../api/api';
import { useAuth } from '../context/AuthContext';
import { Plus, Edit, Trash2, DollarSign, TrendingUp, Clock, CheckCircle } from 'lucide-react';

const ProviderDashboard = () => {
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [wallet, setWallet] = useState({ balance: 0, transactions: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const [servicesRes, bookingsRes, walletRes] = await Promise.all([
        getMyServices(),
        getBookings(),
        getWallet()
      ]);
      setServices(servicesRes.data);
      setBookings(bookingsRes.data);
      setWallet(walletRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalEarnings = bookings
    .filter(b => b.status === 'completed')
    .reduce((sum, b) => sum + (b.amount - b.commission), 0);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Provider Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.full_name}!</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm">Total Earnings</div>
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-2xl font-bold bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">
              ₹{totalEarnings.toFixed(2)}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm">Wallet Balance</div>
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-orange-600">
              ₹{wallet.balance.toFixed(2)}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm">Active Bookings</div>
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {bookings.filter(b => ['pending', 'accepted', 'in_progress'].includes(b.status)).length}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm">Completed</div>
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {bookings.filter(b => b.status === 'completed').length}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="border-b">
            <div className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-2 border-b-2 font-medium transition ${
                  activeTab === 'overview'
                    ? 'border-orange-600 text-orange-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('services')}
                className={`py-4 px-2 border-b-2 font-medium transition ${
                  activeTab === 'services'
                    ? 'border-orange-600 text-orange-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                My Services ({services.length})
              </button>
              <button
                onClick={() => setActiveTab('bookings')}
                className={`py-4 px-2 border-b-2 font-medium transition ${
                  activeTab === 'bookings'
                    ? 'border-orange-600 text-orange-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Bookings ({bookings.length})
              </button>
              <button
                onClick={() => setActiveTab('earnings')}
                className={`py-4 px-2 border-b-2 font-medium transition ${
                  activeTab === 'earnings'
                    ? 'border-orange-600 text-orange-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Earnings
              </button>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
              <div className="space-y-4">
                {bookings.slice(0, 5).map(booking => (
                  <div key={booking.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-semibold">{booking.service?.title}</div>
                      <div className="text-sm text-gray-600">
                        {booking.booking_date} at {booking.booking_time}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-orange-600">₹{booking.amount}</div>
                      <div className="text-sm text-gray-600">{booking.status}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'services' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">My Services</h2>
                <button className="flex items-center space-x-2 bg-gradient-to-r from-orange-500 to-red-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition">
                  <Plus className="w-5 h-5" />
                  <span>Add Service</span>
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {services.map(service => (
                  <div key={service.id} className="border rounded-xl p-6 hover:shadow-lg transition">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-bold text-lg">{service.title}</h3>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-700">
                          <Edit className="w-5 h-5" />
                        </button>
                        <button className="text-red-600 hover:text-red-700">
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{service.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold text-orange-600">₹{service.price}</span>
                      <span className="text-sm text-gray-500">{service.total_bookings} bookings</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'bookings' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">All Bookings</h2>
              <div className="space-y-4">
                {bookings.map(booking => (
                  <div key={booking.id} className="p-6 border rounded-xl hover:shadow-lg transition">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold text-lg mb-2">{booking.service?.title}</h3>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>Customer: {booking.customer?.full_name}</div>
                          <div>Date: {booking.booking_date} at {booking.booking_time}</div>
                          <div>Address: {booking.customer_address}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-orange-600 mb-2">₹{booking.amount}</div>
                        <div className="text-sm text-gray-600 mb-2">Status: {booking.status}</div>
                        {booking.status === 'pending' && (
                          <div className="space-x-2">
                            <button className="text-sm bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                              Accept
                            </button>
                            <button className="text-sm bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
                              Reject
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'earnings' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Earnings & Transactions</h2>
              <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-xl p-8 text-white mb-6">
                <div className="text-sm mb-2">Available Balance</div>
                <div className="text-4xl font-bold mb-4">₹{wallet.balance.toFixed(2)}</div>
                <button className="bg-white text-orange-600 px-6 py-2 rounded-lg font-semibold hover:shadow-lg transition">
                  Withdraw Funds
                </button>
              </div>
              <div className="space-y-3">
                <h3 className="font-bold text-lg mb-4">Recent Transactions</h3>
                {wallet.transactions.map((txn, idx) => (
                  <div key={idx} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-semibold">{txn.description || txn.type}</div>
                      <div className="text-sm text-gray-600">
                        {new Date(txn.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className={`font-bold ${
                      txn.type === 'booking_payment' ? 'text-green-600' : 'text-gray-900'
                    }`}>
                      +₹{txn.amount.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;