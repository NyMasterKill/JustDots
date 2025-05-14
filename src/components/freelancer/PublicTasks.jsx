import { Task } from "../tasks/Task.jsx"
import { useState, useEffect } from "react";
import api from "../../services/api.jsx";
import {useNavigate} from "react-router-dom";

export const PublicTasks = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await api.get('/tasks/tasks/?filter=public');
                setTasks(response.data);
            } catch (err) {
                {err.code == "ERR_BAD_REQUEST" && navigate("/login")};
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
                <div className="blocktitle">лента заказов</div>
                <div>тут пусто</div>
            </>
        )
    }

    return (
        <>
            <div className="hatsaver"></div>
            <div className="blocktitle">лента заказов</div>
            <div className="bodyblock gap10">
                {tasks.map((task) => (
                    <Task key={task.id} task={task} />
                ))}
            </div>
        </>

    )
}

export default PublicTasks