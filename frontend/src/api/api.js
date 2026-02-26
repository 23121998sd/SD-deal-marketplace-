import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Categories
export const getCategories = () => axios.get(`${API_URL}/categories`);

export const createCategory = (data) => 
  axios.post(`${API_URL}/categories`, data, { headers: getAuthHeaders() });

// Services
export const getServices = (params) => axios.get(`${API_URL}/services`, { params });

export const getService = (id) => axios.get(`${API_URL}/services/${id}`);

export const createService = (data) => 
  axios.post(`${API_URL}/services`, data, { headers: getAuthHeaders() });

export const updateService = (id, data) => 
  axios.put(`${API_URL}/services/${id}`, data, { headers: getAuthHeaders() });

export const deleteService = (id) => 
  axios.delete(`${API_URL}/services/${id}`, { headers: getAuthHeaders() });

export const getMyServices = () => 
  axios.get(`${API_URL}/my-services`, { headers: getAuthHeaders() });

// Bookings
export const createBooking = (data) => 
  axios.post(`${API_URL}/bookings`, data, { headers: getAuthHeaders() });

export const getBookings = () => 
  axios.get(`${API_URL}/bookings`, { headers: getAuthHeaders() });

export const getBooking = (id) => 
  axios.get(`${API_URL}/bookings/${id}`, { headers: getAuthHeaders() });

export const updateBookingStatus = (id, status, otp = null) => 
  axios.put(`${API_URL}/bookings/${id}/status`, { status, otp }, { 
    headers: getAuthHeaders(),
    params: { status, otp }
  });

export const createCheckoutSession = (bookingId, originUrl) => 
  axios.post(`${API_URL}/bookings/${bookingId}/checkout`, { origin_url: originUrl }, {
    headers: getAuthHeaders()
  });

export const getCheckoutStatus = (sessionId) => 
  axios.get(`${API_URL}/bookings/checkout/status/${sessionId}`, {
    headers: getAuthHeaders()
  });

// Reviews
export const createReview = (data) => 
  axios.post(`${API_URL}/reviews`, data, { headers: getAuthHeaders() });

export const getServiceReviews = (serviceId) => 
  axios.get(`${API_URL}/reviews/service/${serviceId}`);

export const getProviderReviews = (providerId) => 
  axios.get(`${API_URL}/reviews/provider/${providerId}`);

export const replyToReview = (reviewId, reply) => 
  axios.put(`${API_URL}/reviews/${reviewId}/reply`, { reply }, {
    headers: getAuthHeaders()
  });

// Chat
export const getConversationMessages = (conversationId) => 
  axios.get(`${API_URL}/messages/${conversationId}`, { headers: getAuthHeaders() });

export const getConversations = () => 
  axios.get(`${API_URL}/conversations`, { headers: getAuthHeaders() });

// Wallet & Withdrawals
export const getWallet = () => 
  axios.get(`${API_URL}/wallet`, { headers: getAuthHeaders() });

export const requestWithdrawal = (data) => 
  axios.post(`${API_URL}/withdrawals`, data, { headers: getAuthHeaders() });

export const getWithdrawals = () => 
  axios.get(`${API_URL}/withdrawals`, { headers: getAuthHeaders() });

// Admin
export const getAdminStats = () => 
  axios.get(`${API_URL}/admin/stats`, { headers: getAuthHeaders() });

export const getAllUsers = () => 
  axios.get(`${API_URL}/admin/users`, { headers: getAuthHeaders() });

export const updateUserStatus = (userId, isActive) => 
  axios.put(`${API_URL}/admin/users/${userId}/status`, { is_active: isActive }, {
    headers: getAuthHeaders()
  });

export const processWithdrawal = (withdrawalId, status, adminNotes = null) => 
  axios.put(`${API_URL}/admin/withdrawals/${withdrawalId}`, {
    status,
    admin_notes: adminNotes
  }, { headers: getAuthHeaders() });
