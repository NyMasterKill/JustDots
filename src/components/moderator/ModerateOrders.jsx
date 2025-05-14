import React, {useEffect, useState} from 'react';
import api from "../../services/api.jsx";
import Order from "./Order.jsx";

const ModerateOrders = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await api.get('/tasks/tasks/pending-moderation');
                setTasks(response.data);
            } catch (err) {
                {error.code == 401 && navigate("/login")};
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchTasks();
    }, []);

    if (loading) {
        return (
            <>
                <div className="hatsaver"></div>
                <div className="blocktitle">загрузка заказов...</div>
            </>
        )
    }

    if (error) {
        return (
            <>
                <div className="hatsaver"></div>
                <div>Ошибка: {error.message || "неизвестная"}</div>
            </>
        )
    }

    if (tasks.length === 0) {
        return (
            <>
                <div className="hatsaver"></div>
                <div className="blocktitle">модерация заказов</div>
                <div>Новых заказов нет</div>
            </>
        )
    }

    return (
        <>
            <div className="hatsaver"></div>
            <div className="blocktitle">модерация заказов</div>
            <div className="bodyblock gap10">
                {tasks.map((task) => (
                    <Order key={task.id} task={task} />
                ))}
            </div>
        </>

    )
};

export default ModerateOrders;