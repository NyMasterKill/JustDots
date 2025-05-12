import { useState, useEffect, useContext } from 'react';
import { useNotification } from '../context/Notifications.jsx';
import { Navigate, useParams } from 'react-router-dom';
import exampleimage from '../assets/UI/photoexample.jpg'
import api from '../services/api';
import Loader from './Loader.jsx';
import { AuthContext } from '../context/AuthContext.jsx';
import ratingstar from '../assets/ICONS/RATINGSTAR.svg'
import simpleuser from '../assets/ICONS/SIMPLEUSER.svg'
import timestamp from '../assets/ICONS/TIMESTAMP.svg'
import { useNavigate } from 'react-router-dom';
import SimpleHatButton from '../components/SimpleHatButton.jsx';
import SimpleButton from './SimpleButton.jsx';
import { CalcDater } from '../utils/CalcDater.jsx';
import Modal from './Modal.jsx';
import { SERVER_URL } from '../pathconfig.js';

const Profile = () => {
    const { id } = useParams();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { myuser } = useContext(AuthContext);
    const notify = useNotification();
    const navigate = useNavigate();

    const handleAvatarUploader = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const MAX_SIZE = 5 * 1024 * 1024;
        if (!['image/jpeg', 'image/png'].includes(file.type) || file.size > MAX_SIZE) {
            notify({
                message: 'Файл должен быть JPG/PNG (макс. 5MB)',
                type: "error",
                duration: 4200
            });
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('avatar', file);

            const response = await api.put("/users/profile/avatar", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            notify({
                message: "Аватар обновлен!",
                type: "success",
                duration: 3000
            });

        } catch (err) {
            notify({
                message: err.response?.data?.message || "Ошибка загрузки",
                type: "error",
                duration: 4200
            });
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        const Fetcher = async () => {
            try {
                setLoading(true);
                const response = await api.get(`/users/profile/${id}`);
                setProfile(response.data);
            } catch (error) {
                console.error('Ошибка при получении профиля: ', error)
                setProfile(myuser);
                notify({ message: "Ошибка при получении профиля", type: "error", duration: 4200 });
                navigate("/profile/" + myuser.id);
            }
            finally {
                setLoading(false);
            }
        };
        Fetcher();
    }, [id])

    if (loading) {
        return <Loader></Loader>
    }



    const { daysDiff, dayText } = CalcDater(profile.created_at);
    console.log(profile);
    return (
        <>
            <div className='hatsaver'></div>
            <div className='blocktitle'>
                {profile && profile.id === myuser.id ? "мой профиль" : "профиль пользователя "}
            </div>
            <div className='bodyblock'>
                <div className='filler'>
                    <div className='ellipse-profile'>
                        {profile && profile.id === myuser.id ? (
                            <>
                                <input style={{ display: "none" }} type="file" accept=".jpg,.jpeg,.png" id="profileimguploader" onChange={handleAvatarUploader}></input>
                                <label htmlFor='profileimguploader' title='Нажмите чтобы загрузить новое фото' className='ellipse-hoverer' />
                                <img
                                    className='iph'
                                    src={myuser.profile?.avatar_url ? `${SERVER_URL + profile.profile?.avatar_url}` : null}
                                />
                            </>
                        ) : (
                            <>
                                <img src={profile.profile?.avatar_url ? `${SERVER_URL + profile.profile?.avatar_url}` : null} />
                            </>
                        )}
                    </div>
                    <div className='profile-info'>
                        <div className='profile-info-name'>
                            <span>{profile.username}</span>
                            <div className='ellipse'></div>
                            <div className='ellipse'></div>
                            <div className='ellipse'></div>
                        </div>
                        <div className='profile-info-work'>
                            {profile.user_type == "customer" ?
                                (
                                    <div className='propblock black'>
                                        Заказчик
                                    </div>
                                ) : (
                                    <div className='propblock'>
                                        Исполнитель
                                    </div>
                                )
                            }
                            <div className={"propblock black"}>
                                <img src={ratingstar} alt="" />
                                {profile.rating || "0.0"}
                            </div>
                            <div className='propblock accent'>
                                {profile.completed_tasks_count} {profile.user_type == "freelancer" ? "выполненных" : "завершённых"} заказов
                            </div>
                        </div>
                        <div className='profile-info-sub'>
                            <div className='simplepropblock'>
                                <img style={{ height: 20 + "px" }} src={simpleuser} alt="simpleuser" />
                                {profile.last_name} {profile.first_name} {profile.patronymic}
                            </div>
                            <div className='simplepropblock'>
                                <img style={{ height: 20 + "px" }} src={timestamp} alt="timestamp" />
                                на justdots {daysDiff} {dayText}
                            </div>
                        </div>
                    </div>
                    <div className='profile-edit-container'>
                        {myuser.id == profile.id ? (
                            <SimpleButton icon='edit'>Редактировать профиль</SimpleButton>
                        ) : (
                            null
                        )}
                    </div>
                </div>
                <div style={{ paddingTop: 25 + "px" }} className='titleblock'>
                    Обо мне
                </div>
                <div className='textblock'>
                    {profile.profile?.bio || "Тут пусто"}
                </div>
            </div>
            <div className='bodyblock'>
                <div className='titleblock'>
                    Навыки
                </div>
                <div className='textblock'>
                    Тут пусто
                </div>
                <div style={{ paddingTop: 25 + "px" }} className='titleblock'>
                    Портфолио
                </div>
                <div className='textblock'>
                    Тут пусто
                </div>
            </div>

            <div className='bodyblock black'>

            </div>
        </>
    );
};

export default Profile;