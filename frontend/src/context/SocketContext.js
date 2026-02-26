import React, { createContext, useState, useContext, useEffect } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from './AuthContext';

const SocketContext = createContext();

const SOCKET_URL = process.env.REACT_APP_BACKEND_URL;

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState({});
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      const socketInstance = io(SOCKET_URL, {
        path: '/socket.io/',
        transports: ['websocket', 'polling']
      });

      socketInstance.on('connect', () => {
        console.log('Socket connected');
        socketInstance.emit('register_user', { user_id: user.id });
      });

      socketInstance.on('new_message', (message) => {
        setMessages(prev => [...prev, message]);
      });

      socketInstance.on('message_sent', (message) => {
        setMessages(prev => [...prev, message]);
      });

      setSocket(socketInstance);

      return () => {
        socketInstance.disconnect();
      };
    }
  }, [user]);

  const sendMessage = (receiverId, message, bookingId = null) => {
    if (socket && user) {
      socket.emit('send_message', {
        sender_id: user.id,
        receiver_id: receiverId,
        message,
        booking_id: bookingId
      });
    }
  };

  const markAsRead = (conversationId) => {
    if (socket && user) {
      socket.emit('mark_read', {
        conversation_id: conversationId,
        user_id: user.id
      });
    }
  };

  return (
    <SocketContext.Provider value={{ socket, messages, sendMessage, markAsRead, onlineUsers }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => useContext(SocketContext);
