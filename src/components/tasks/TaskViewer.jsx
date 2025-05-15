import { useParams } from "react-router-dom";
import { useEffect, useState, useContext } from "react";
import { useNotification } from '../../context/Notifications.jsx';
import { AuthContext } from '../../context/AuthContext.jsx';
import api from '../../services/api.jsx';
import { CalcMinusDater } from '../../utils/CalcMinusDater.jsx';
import { AutoTextarea } from "../other/AutoTextarea.jsx";
import { SimpleButton } from "../SimpleButton.jsx";
import { Link, useNavigate } from "react-router-dom";
import { SERVER_URL } from "../../pathconfig.js";
import Loader from '../Loader.jsx';
import FeedbacksViewer from "../customer/FeedbacksViewer.jsx";
import {getAppCounter} from "../../utils/AppCounter.jsx";
import TaskBudjet from "./TaskBudjet.jsx";
import TaskStatus from "./TaskStatus.jsx";
import MakeReview from "./MakeReview.jsx";
import Icon from "../other/Icon.jsx";
import ReviewViewer from "./ReviewViewer.jsx";

export const TaskViewer = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const { myuser } = useContext(AuthContext);
    const [loading, setLoading] = useState(true);
    const [task, setTask] = useState(0);
    const notify = useNotification();
    const [taskOwner, setTaskOwner] = useState({});
    const [taskFreelancer, setTaskFreelancer] = useState({});
    const [appcounter, setApps] = useState(0);
    const [isConfirmed, setConfirm] = useState(false);

    const handleTaskFetch = async () => {
        if (!myuser) return;
        try {
            const taskResponse = await api.get(`/tasks/tasks/${id}`);
            setTask(taskResponse.data);

            if (taskResponse.data.owner_id) {
                const ownerResponse = await api.get(`/users/profile/${taskResponse.data.owner_id}`);
                setTaskOwner(ownerResponse.data);
            }

            if (taskResponse.data.freelancer_id) {
                const freelancerResponse = await api.get(`/users/profile/${taskResponse.data.freelancer_id}`);
                setTaskFreelancer(freelancerResponse.data);
            }

            if(!task.freelancer_id && myuser.user_type !== "customer"){
                const count = await getAppCounter(task.id);
                setApps(count);
            }
        } catch (error) {
            {error.code == "ERR_BAD_REQUEST" && navigate("/login")};
            console.error('Ошибка при загрузке данных:', error);
            notify({ message: "Ошибка при загрузке данных", type: "error", duration: 4200 });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        handleTaskFetch();
    }, [id, isConfirmed]);

    const handleTaskDelete = async () => {
        try {
            await api.delete(`/tasks/tasks/${task.id}`);
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
            await api.post(`/tasks/tasks/${task.id}/close`);
            notify({ message: `Заказ #${task.id} завершен`, type: "success", duration: 4200 });
            handleTaskFetch();
        }
        catch (error) {
            console.log(error);
            notify({ message: `Ошибка при завершении заказа: ${error.message || "NuN"}`, type: "error", duration: 4200 });
        }
    }

    const handleSendApp = async () => {
        const nowdate = new Date().toISOString();
        try {
            await api.post(`/tasks/tasks/${task.id}/apply`, { comment: "test", proposed_price: 100, proposed_deadline: `${nowdate}` })
            notify({ message: `Вы подали заявку на выполнение заказа #${task.id}`, type: "info", duration: 4200 });
        }
        catch (error) {
            console.log(error);
            notify({ message: `${error.response?.data?.detail || "Ошибка при подаче заявки"}`, type: "error", duration: 4200 });
        }
    }

    const handleConfirm = () => {
        setConfirm(true);
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
                <SimpleButton icon="arrow-left" onClick={() => navigate(-1)}>Назад</SimpleButton>
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
                            <TaskBudjet bmin={task.budget_min} bmax={task.budget_max} view="max"/>
                            <TaskStatus status={task.status}/>
                        </div>
                    </div>
                    <div className="taskblock">
                        {myuser.id === taskOwner.id && task.status !== "На рассмотрении модерацией" ? (
                            <div className="tbtop">
                                {task.status === "Открытая" || task.status === "Отклонена модерацией" ? (
                                    <SimpleButton style="red" icon="trash" onClick={handleTaskDelete}>
                                        Удалить заказ
                                    </SimpleButton>
                                ) : (
                                    <div className="task-freelancerlinkfull">
                                        <span>{task.status === "В процессе" ? "В работе у" : "Заказ выполнил"}</span>
                                        <Link style={{ textDecoration: "none" }} to={`/profile/${taskFreelancer.id}`}>
                                            <div className="miniprofile">
                                                {taskFreelancer.username}
                                                <div className="miniprofile-avatar">
                                                    {taskFreelancer?.profile?.avatar_url ? (
                                                        <img src={`${SERVER_URL}${taskFreelancer.profile.avatar_url}`} alt="Аватар фрилансера" />
                                                    ) : (<div/>)}
                                                </div>
                                            </div>
                                        </Link>
                                    </div>
                                )}
                            </div>
                        ) : task.status !== "На рассмотрении модерацией" ? (
                            <div className="tbtop">
                                <div className="task-freelancerlinkfull">
                                    <span>Заказчик</span>
                                    <Link style={{ textDecoration: "none" }} to={`/profile/${taskOwner.id}`}>
                                        <div className="miniprofile">
                                            {taskOwner.username}
                                            <div className="miniprofile-avatar">
                                                {taskOwner?.profile?.avatar_url ? (
                                                    <img src={`${SERVER_URL}${taskOwner.profile.avatar_url}`} alt="Аватар заказчика" />
                                                ) : (<div/>)}
                                            </div>
                                            <div className="propblock black">
                                                <Icon icon="star" color="gold"/>
                                                {taskOwner.profile?.rating || "0.0"}
                                            </div>
                                        </div>
                                    </Link>
                                </div>
                            </div>
                        ) : task.status === "На рассмотрении модерацией" && (
                            <div className="tbtop">
                                <SimpleButton style="red" icon="trash" onClick={handleTaskDelete}>
                                    Удалить заказ
                                </SimpleButton>
                            </div>
                        )}
                        {myuser.user_type == "freelancer" ? (
                            <>
                                {task.status == "Открытая" && (
                                <div className="tbbottom">
                                    <SimpleButton icon="user" style="accent" onClick={handleSendApp}>
                                        Откликнуться
                                    </SimpleButton>
                                </div>
                                )}
                            </>
                        ) : (
                            <div className="tbbottom">
                                {task.status == "В процессе" && (
                                    <SimpleButton style="accent" onClick={handleConfirmTask}>
                                        Подтвердить выполнение заказа
                                    </SimpleButton>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {task.status == "Закрытая" && (
                    <ReviewViewer taskOwner={taskOwner} taskFreelancer={taskFreelancer} task={task} myuser={myuser}/>
                )}

                {task.status == "Открытая" && myuser.user_type !== "freelancer" ? (
                    <FeedbacksViewer task={task} user={myuser.user_type} onConfirm={handleConfirm}></FeedbacksViewer>
                ) : null}

                {task.status === "Закрытая" && (
                    <>
                        {taskOwner.id === myuser.id && !task.customer_review ?(
                            <MakeReview task={task} taskowner={taskOwner} taskfreelancer={taskFreelancer}/>
                        ) : taskFreelancer.id === myuser.id && !task.freelancer_review && (
                            <MakeReview task={task} taskowner={taskOwner} taskfreelancer={taskFreelancer}/>
                        )}
                    </>
                )}
            </div >
        </>
    )
}

export default TaskViewer