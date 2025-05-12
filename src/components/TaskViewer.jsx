import { useParams } from "react-router-dom";
import { useEffect, useState, useContext, useRef } from "react";
import { useNotification } from '../context/Notifications.jsx';
import rubleicon from "../assets/ICONS/RUBLE.svg";
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';
import { CalcMinusDater } from '../utils/CalcMinusDater';
import { AutoTextarea } from "./other/AutoTextarea.jsx";
import { SimpleButton } from "../components/SimpleButton.jsx";
import { Link, useNavigate } from "react-router-dom";
import ratingstar from '../assets/ICONS/RATINGSTAR.svg'
import { SERVER_URL } from "../pathconfig.js";
import Loader from './Loader.jsx';
import Feedback from "./customer/Feedback.jsx";


export const TaskViewer = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const { myuser } = useContext(AuthContext);
    const [loading, setLoading] = useState(false);
    const [task, setTask] = useState(1);
    const [appcounter, setAppCounter] = useState(0);
    const [taskcounterapp, setTaskAppCounter] = useState([]);
    const notify = useNotification();
    const [taskOwner, setTaskOwner] = useState({});
    const [taskFreelancer, setTaskFreelancer] = useState({});

    const handleTaskFetch = async () => {
        if (!myuser) return;
        const currentroute = myuser.user_type == "customer" ? `/tasks/tasks/${id}` : `/tasks/tasks/${id}/public`;
        try {
            setLoading(true);
            const response = await api.get(currentroute);
            setTask(response.data);
        } catch (error) {
            setLoading(false);
            console.log(error);
            navigate(`/profile/${myuser.id}`);
            notify({ message: "Такого заказа не существует", type: "error", duration: 4200 });
        }
        finally {
            setLoading(false);
        }

        if (myuser.user_type == "customer") {
            try {
                setLoading(true);
                const counterresponse = await api.get(`/tasks/tasks/${id}/applications`);
                setTaskAppCounter(counterresponse.data);
            } catch (error) {
                setLoading(false);
                console.log(error);
            }
            finally {
                setLoading(false);
            }
        }
    };

    useEffect(() => {

        handleTaskFetch();
    }, [myuser])

    useEffect(() => {
        setAppCounter(taskcounterapp.length || 0);
    }, [taskcounterapp])

    //ПОЛУЧЕНИЕ ЗАКАЗЧИКА ЗАДАЧИ (ДЛЯ ФРИЛАНСЕРА) || ПОЛУЧЕНИЕ ФРИЛАНСЕРА (ДЛЯ ЗАКАЗЧИКА)
    useEffect(() => {
        const fetchTaskOwner = async () => {
            if (!task || !task.owner_id) return;
            try {
                const response = await api.get(`/users/profile/${task.owner_id}`);
                setTaskOwner(response.data);
            } catch (error) {
                console.error('Ошибка при получении профиля:', error);
            }
        };

        const fetchFreelancer = async () => {
            if (!task || !task.freelancer_id) return;

            try {
                const response = await api.get(`/users/profile/${task.freelancer_id}`);
                setTaskFreelancer(response.data);
            } catch (error) {
                console.error('Ошибка при получении профиля:', error);
            }

        }

        fetchTaskOwner();
        fetchFreelancer();
    }, [task]);

    const handleTaskDelete = async () => {
        try {
            const response = await api.delete(`/tasks/tasks/${task.id}`);
            notify({ message: `Заказ #${task.id} удален`, type: "info", duration: 4200 });
        }
        catch (error) {
            console.log(error);
            notify({ message: `Ошибка при удалении заказа: ${error.message || "NuN"}`, type: "error", duration: 4200 });
        }
        finally {
            navigate("/mytasks")
        }
    }

    const handleConfirmTask = async () => {
        try {
            const confirmresponse = await api.post(`/tasks/tasks/${task.id}/close`);
            notify({ message: `Заказ #${task.id} завершен`, type: "success", duration: 4200 });
        }
        catch (error) {
            console.log(error);
            notify({ message: `Ошибка при завершении заказа: ${error.message || "NuN"}`, type: "error", duration: 4200 });
        }
        finally {
            handleTaskFetch();
        }
    }

    const handleSendApp = async () => {
        const nowdate = new Date().toISOString();
        try {
            const sendresponse = await api.post(`/tasks/tasks/${task.id}/apply`, { comment: "test", proposed_price: 100, proposed_deadline: `${nowdate}` })
            notify({ message: `Вы подали заявку на выполнение заказа #${task.id}`, type: "info", duration: 4200 });
        }
        catch (error) {
            console.log(error);
            notify({ message: `Ошибка при подаче заявки: ${error.message || "NuN"}`, type: "error", duration: 4200 });
        }
        finally {
            handleTaskFetch();
        }
    }

    if (loading) {
        return (
            <Loader />
        )
    }

    const { diffresult, dayText, status } = CalcMinusDater(task.deadline);
    return (
        <>
            <div className='hatsaver'></div>
            <div className='blocktitle'>
                <SimpleButton icon="backc" onClick={() => navigate(-1)}>Назад</SimpleButton>
                заказ #{task.id}
                <SimpleButton style="black" onClick={() => console.log(task)}>DEBUG: Получить тело задачи (console)</SimpleButton>
            </div>
            <div className="bodyblock gap10">
                <div className="bodyblock fxrow">
                    <div className="taskblock-insp">
                        <div className="taskblock-title">
                            {task.title}
                        </div>
                        <div className="taskblock-info">
                            <div className="taskblock-infoprops">
                                <div className="propblock accent">
                                    {task.category}
                                </div>
                                <div className="propblock">
                                    Опыт работы: {task.skill_level}
                                </div>
                                {task.status == "Открытая" ? (
                                    <div className={status ? "propblock black" : "propblock red"}>
                                        Срок: {diffresult} {dayText}
                                    </div>
                                ) : task.status == "В процессе" ? (
                                    <div className={status ? "propblock black" : "propblock red"}>
                                        Срок: {diffresult} {dayText}
                                    </div>
                                ) : null}
                            </div>
                            <AutoTextarea>{task.description}</AutoTextarea>
                            <div className="propblock taskblock-price">
                                {task.budget_max !== task.budget_min ? (
                                    <>
                                        {task.budget_min} - {task.budget_max}
                                        < img style={{ height: 22 + "px" }} src={rubleicon}></img>
                                        <span style={{ fontSize: 17 + "px", paddingTop: 5 + "px" }}>за заказ</span>
                                    </>
                                ) : (
                                    <>
                                        {task.budget_max}
                                        < img style={{ height: 22 + "px" }} src={rubleicon}></img>
                                        <span style={{ fontSize: 17 + "px", paddingTop: 5 + "px" }}>за заказ</span>
                                    </>
                                )}

                            </div>
                            <div className="tblbottom">
                                <div className={task.status == "Открытая" ? "propblock" : task.status == "В процессе" ? "propblock" : "propblock black"}>
                                    {
                                        task.status == "Закрытая" ? (
                                            <span style={{ color: "white", fontSize: 14 + "px", fontWeight: 800 }}>{task.status}</span>
                                        ) : task.status == "В процессе" ? (
                                            <>
                                                <span style={{ color: "black", fontSize: 14 + "px", fontWeight: 800 }}>{task.status}</span>
                                            </>
                                        ) : (
                                            <>
                                                <div style={{ width: 10 + "px", height: 10 + "px", background: "limegreen" }} className="ellipse"></div>
                                                <span style={{ color: "limegreen", fontSize: 14 + "px", fontWeight: 800 }}>{task.status}</span>
                                            </>
                                        )
                                    }
                                </div>
                            </div>
                        </div>
                        <div className="taskblock-attr">

                        </div>
                    </div>
                    <div className="taskblock">
                        {myuser.user_type == "customer" ? (
                            <div className="tbtop">
                                {task.status === "Открытая" && appcounter == 0 ? (
                                    <SimpleButton style="red" icon="x" onClick={handleTaskDelete}>Удалить заказ</SimpleButton>
                                ) : task.status === "Открытая" && appcounter > 0 ? (
                                    null
                                ) : task.status === "В процессе" ? (
                                    <>

                                        <div className="task-freelancerlinkfull">
                                            <span>В работе у</span>
                                            <Link style={{ textDecoration: "none" }} to={"/profile/" + taskFreelancer.id}>
                                                <div className="miniprofile">
                                                    {taskFreelancer.username}
                                                    <div className="miniprofile-avatar">
                                                        {taskFreelancer?.profile?.avatar_url ? (
                                                            <img src={SERVER_URL + (taskFreelancer.profile?.avatar_url || null)}></img>
                                                        ) : (
                                                            <div></div>
                                                        )}
                                                    </div>
                                                </div>
                                            </Link>
                                        </div>

                                    </>
                                ) : (
                                    <>

                                        <div className="task-freelancerlinkfull">
                                            <span>Заказ выполнил</span>
                                            <Link style={{ textDecoration: "none" }} to={"/profile/" + taskFreelancer.id}>
                                                <div className="miniprofile">
                                                    {taskFreelancer.username}
                                                    <div className="miniprofile-avatar">
                                                        {taskFreelancer?.profile?.avatar_url ? (
                                                            <img src={SERVER_URL + (taskFreelancer?.profile?.avatar_url || null)}></img>
                                                        ) : (
                                                            <div></div>
                                                        )}
                                                    </div>
                                                </div>
                                            </Link>
                                        </div>

                                    </>
                                )}

                            </div>
                        ) : (
                            <div className="tbtop">
                                <div className="task-freelancerlinkfull">
                                    <span>Заказчик</span>
                                    <Link style={{ textDecoration: "none" }} to={"/profile/" + taskOwner.id}>
                                        <div className="miniprofile">
                                            {taskOwner.username}
                                            <div className="miniprofile-avatar">
                                                {taskOwner?.profile?.avatar_url ? (
                                                    <img src={SERVER_URL + (taskOwner?.profile?.avatar_url || null)}></img>
                                                ) : (
                                                    <div></div>
                                                )}
                                            </div>
                                            <div className="propblock black">
                                                <img src={ratingstar} alt="" />
                                                {taskOwner.profile?.rating || "0.0"}
                                            </div>
                                        </div>
                                    </Link>
                                </div>
                            </div>
                        )}
                        {myuser.user_type == "freelancer" ? (
                            <div className="tbbottom">
                                <SimpleButton style="accent" onClick={handleSendApp}>
                                    Откликнуться
                                </SimpleButton>
                            </div>
                        ) : (
                            <div className="tbbottom">
                                {task.status == "Открытая" && myuser.user_type == "customer" ? (
                                    <SimpleButton
                                        style={appcounter > 0 ? "white butcounter" : "white"}
                                        data-count={appcounter}
                                    >
                                        Заявки
                                    </SimpleButton>
                                ) : task.status == "В процессе" ? (
                                    <SimpleButton style="accent" onClick={handleConfirmTask}>
                                        Подтвердить выполнение заказа
                                    </SimpleButton>
                                ) : (
                                    null
                                )}
                            </div>
                        )}
                    </div>


                </div>

                <div className="bodyblock gap10">
                    <div className="titleblock">
                        {`Заявки (${appcounter})`}
                    </div>
                    <Feedback taskid={task.id}></Feedback>
                </div>
            </div >
        </>
    )
}

export default TaskViewer