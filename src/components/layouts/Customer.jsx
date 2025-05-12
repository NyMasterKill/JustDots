import { useState, useContext, Children } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { Navigate, useNavigate, Outlet, Route, Router } from 'react-router-dom';

export const Customer = () => {
    const { myuser } = useContext(AuthContext);

    if (myuser.user_type == "freelancer") {
        return <Navigate to={"/profile/" + myuser.id} />
    }


    return (
        <>
            <Outlet />
        </>
    );
}

export default Customer