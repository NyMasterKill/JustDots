import { Task } from "./Task"
import { useState, useEffect } from "react";
import api from "../services/api";
import SimpleButton from "./SimpleButton";
import { Link } from "react-router-dom";

export const MyTasks = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await api.get('/tasks/tasks');
                setTasks(response.data);
            } catch (err) {
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
                <div className="blocktitle">мои заказы</div>
                <div>Вы ещё не создавали заказы</div>
                <Link to="/create">
                    <SimpleButton style="black" icon="plus">Создать заказ</SimpleButton>
                </Link>
            </>
        )
    }

    return (
        <>
            <div className="hatsaver"></div>
            <div className="blocktitle">мои заказы</div>
            <div className="bodyblock gap10">
                {tasks.map((task) => (
                    <Task key={task.id} taskid={task.id} />
                ))}
            </div>
        </>

    )
}

export default MyTasks