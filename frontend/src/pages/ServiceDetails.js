import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getService, getServiceReviews, createBooking } from '../api/api';
import { useAuth } from '../context/AuthContext';
import { Star, Clock, MapPin, Award, ArrowLeft } from 'lucide-react';

const ServiceDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [service, setService] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingData, setBookingData] = useState({
    booking_date: '',
    booking_time: '',
    customer_address: '',
    notes: ''
  });
  const [bookingLoading, setBookingLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [serviceRes, reviewsRes] = await Promise.all([
        getService(id),
        getServiceReviews(id)
      ]);
      setService(serviceRes.data);
      setReviews(reviewsRes.data);
    } catch (error) {
      console.error('Failed to fetch service:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!user) {
      navigate('/auth?mode=login');
      return;
    }

    if (user.role !== 'customer') {
      alert('Only customers can book services!');
      return;
    }

    setBookingLoading(true);
    try {
      const response = await createBooking({
        service_id: id,
        ...bookingData
      });
      
      // Redirect to payment
      const originUrl = window.location.origin;
      navigate(`/booking/${response.data.booking_id}/payment?origin=${originUrl}`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Booking failed');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Service not found</h2>
          <Link to="/services" className="text-orange-600 hover:text-orange-700">Browse Services</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Link to="/services" className="flex items-center text-gray-600 hover:text-orange-600 mb-6">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Services
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Service Info */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="text-sm text-orange-600 font-semibold mb-2">
                    {service.category?.icon} {service.category?.name}
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{service.title}</h1>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                      <span className="font-semibold">{service.rating.toFixed(1)}</span>
                      <span className="ml-1">({service.total_bookings} bookings)</span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {service.duration_minutes} minutes
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold bg-gradient-to-r from-orange-500 to-red-600 bg-clip-text text-transparent">
                    ₹{service.price}
                  </div>
                  <div className="text-sm text-gray-500">per service</div>
                </div>
              </div>

              <div className="border-t pt-6 mt-6">
                <h3 className="font-bold text-lg mb-3">Description</h3>
                <p className="text-gray-700 leading-relaxed">{service.description}</p>
              </div>

              {/* Provider Info */}
              {service.provider && (
                <div className="border-t pt-6 mt-6">
                  <h3 className="font-bold text-lg mb-4">Service Provider</h3>
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 rounded-full flex items-center justify-center text-white text-2xl">
                      {service.provider.full_name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-lg">{service.provider.full_name}</div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                        {service.provider.rating.toFixed(1)} • {service.provider.total_reviews} reviews
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Reviews */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h3 className="font-bold text-2xl mb-6">Customer Reviews</h3>
              {reviews.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No reviews yet. Be the first to review!</p>
              ) : (
                <div className="space-y-6">
                  {reviews.map(review => (
                    <div key={review.id} className="border-b pb-6 last:border-b-0">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                            {review.customer?.full_name.charAt(0)}
                          </div>
                          <div>
                            <div className="font-semibold">{review.customer?.full_name}</div>
                            <div className="flex items-center text-sm">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-4 h-4 ${
                                    i < review.overall_rating
                                      ? 'text-yellow-400 fill-current'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                              <span className="ml-2 text-gray-600">{review.overall_rating.toFixed(1)}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(review.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      {review.comment && (
                        <p className="text-gray-700 mb-3">{review.comment}</p>
                      )}
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-gray-600">Behavior:</span>
                          <span className="ml-2 font-semibold">{review.ratings.behavior}/5</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Punctuality:</span>
                          <span className="ml-2 font-semibold">{review.ratings.punctuality}/5</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Quality:</span>
                          <span className="ml-2 font-semibold">{review.ratings.quality}/5</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Value:</span>
                          <span className="ml-2 font-semibold">{review.ratings.value_for_money}/5</span>
                        </div>
                      </div>
                      {review.provider_reply && (
                        <div className="mt-3 ml-8 p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm font-semibold text-gray-700 mb-1">Provider Reply:</div>
                          <p className="text-sm text-gray-600">{review.provider_reply}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Booking Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-4">
              <h3 className="font-bold text-xl mb-4">Book This Service</h3>
              <form onSubmit={handleBooking} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                  <input
                    type="date"
                    value={bookingData.booking_date}
                    onChange={(e) => setBookingData({ ...bookingData, booking_date: e.target.value })}
                    min={new Date().toISOString().split('T')[0]}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    data-testid="booking-date-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Time</label>
                  <input
                    type="time"
                    value={bookingData.booking_time}
                    onChange={(e) => setBookingData({ ...bookingData, booking_time: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    data-testid="booking-time-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Your Address</label>
                  <textarea
                    value={bookingData.customer_address}
                    onChange={(e) => setBookingData({ ...bookingData, customer_address: e.target.value })}
                    required
                    rows={3}
                    placeholder="Enter your complete address"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    data-testid="booking-address-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Special Instructions (Optional)</label>
                  <textarea
                    value={bookingData.notes}
                    onChange={(e) => setBookingData({ ...bookingData, notes: e.target.value })}
                    rows={2}
                    placeholder="Any specific requirements?"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-600">Service Charge:</span>
                    <span className="font-semibold">₹{service.price}</span>
                  </div>
                  <div className="flex justify-between mb-4">
                    <span className="text-gray-900 font-bold">Total:</span>
                    <span className="text-xl font-bold bg-gradient-to-r from-orange-500 to-red-600 bg-clip-text text-transparent">
                      ₹{service.price}
                    </span>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={bookingLoading}
                  className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50"
                  data-testid="book-now-button"
                >
                  {bookingLoading ? 'Processing...' : 'Book Now & Pay'}
                </button>

                <p className="text-xs text-gray-500 text-center">
                  Payment will be held securely until service completion
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetails;