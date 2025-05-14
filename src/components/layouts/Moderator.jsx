import { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { Navigate, Outlet } from 'react-router-dom';
import Loader from '../Loader.jsx';

export const Moderator = () => {
    const {myuser, isAuthenticated, loading } = useContext(AuthContext);

    if(myuser?.user_type !== "moderator") return (
        <Navigate to={`/profile/${myuser?.id}`}></Navigate>
    );

    if (loading) {
        return <Loader></Loader>
    }
    if (!isAuthenticated) {
        return <Navigate to="/login" />
    }

    return (
        <>
            <div className='main-container'>
                <Outlet />
            </div>
        </>
    );
}