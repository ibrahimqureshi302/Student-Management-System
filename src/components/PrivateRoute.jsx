import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children, user }) => {
    const token = localStorage.getItem('access_token');
    
    if (!token && !user) {
        return <Navigate to="/login" replace />;
    }
    
    return children;
};

export default PrivateRoute;