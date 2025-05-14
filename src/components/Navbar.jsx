import { useContext } from 'react';
import {Link, useNavigate} from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import SimpleButton from './SimpleButton';
import LogoContainer from './LogoContainer';
import exampleimage from '../assets/UI/photoexample.jpg'
import searchico from '../assets/ICONS/SEARCH.svg'
import SimpleHatButton from './SimpleHatButton';
import { SERVER_URL } from '../pathconfig.js';

const Navbar = () => {
    const navigate = useNavigate();
    const { myuser, isAuthenticated, logout } = useContext(AuthContext);
    const handleLogout = async () => {
        await logout();
        navigate("/login");
    };

    return (
        <>
            <div className="hat">
                <div className="hat-container">
                    <LogoContainer size="littl" />
                    <nav className='hat-interactive-menu'>
                        {!isAuthenticated ?(
                            <>  {/* ШАПКА ПРИ АНОНИМЕ */}
                                <Link style={{ textDecoration: 'none' }} to="/login">
                                    <SimpleButton style={"white"}>Вход</SimpleButton>
                                </Link>
                                <Link style={{ textDecoration: 'none' }} to="/register">
                                    <SimpleButton style={"black"}>Регистрация</SimpleButton>
                                </Link>
                            </>
                        ) : isAuthenticated && myuser.user_type !== "moderator" ?(
                            <>  {/* ШАПКА ПРИ АВТОРИЗАЦИИ */}
                                <div className='hat-interactive-menu-act'>
                                    {myuser.user_type == "freelancer" ? (
                                        <Link style={{textDecoration: "none"}} to="/orders">
                                            <SimpleButton icon="search">Лента заказов</SimpleButton>
                                        </Link>
                                    ) : (
                                        <Link style={{textDecoration: "none"}} to="/create">
                                            <SimpleButton style="black" icon="plus">Создать заказ</SimpleButton>
                                        </Link>
                                    )}
                                    <SimpleButton icon="arbitrage">Арбитраж</SimpleButton>
                                    <SimpleButton style="accent" icon="support">Техн. поддержка</SimpleButton>
                                </div>
                                <Link style={{textDecoration: "none"}} to={"/mytasks"}>
                                    <SimpleButton icon="order" title="Мои заказы">Мои заказы</SimpleButton>
                                </Link>
                                <SimpleHatButton icon="messages">Сообщения</SimpleHatButton>
                                <Link style={{ textDecoration: 'none' }} to={"/profile/" + myuser.id} title='Мой профиль'>
                                    <div tabIndex={0} className='ellipse-profile miniep'>
                                        <img src={myuser.profile?.avatar_url ? `${SERVER_URL + myuser.profile?.avatar_url}` : null} />
                                    </div>
                                </Link>
                                <SimpleHatButton isActive="true" icon="logout" title="Выйти из аккаунта" onClick={handleLogout}></SimpleHatButton>
                            </>
                        ) : (
                            <>
                                <div className="hat-interactive-menu-act">
                                    <div className="moderator-hat-title">
                                        moderator
                                    </div>
                                    <Link style={{textDecoration: "none"}} to="/moderate">
                                        <SimpleButton icon="search" style="accent">Модерация заказов</SimpleButton>
                                    </Link>
                                </div>
                                {myuser.username}
                                <SimpleHatButton isActive="true" icon="logout" title="Выйти из аккаунта" onClick={handleLogout}></SimpleHatButton>
                            </>
                    )}
                    </nav>
                </div>
            </div >
        </>
    );
};

export default Navbar;