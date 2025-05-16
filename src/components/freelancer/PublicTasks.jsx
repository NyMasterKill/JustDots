import { Task } from "../tasks/Task.jsx"
import { useState, useEffect } from "react";
import api from "../../services/api.jsx";
import {useNavigate} from "react-router-dom";
import SimpleButton from "../SimpleButton.jsx";

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

    return (
        <>
            <div className="hatsaver"></div>
            <div className="blocktitle">лента заказов</div>
            <div className="bodyblock gap10">
                <div className="bfxrow gap5">
                    <SimpleButton style="black" icon="sort">Сортировать по</SimpleButton>
                    <SimpleButton style="black" icon="filter">Фильтр</SimpleButton>
                    <SimpleButton style="accent" icon="refresh"></SimpleButton>
                </div>
            {tasks.length > 0 ? (
                <>
                    {tasks.map((task) => (
                        <Task key={task.id} task={task} />
                    ))}
                </>
            ) : "новых заказов нет"}
            </div>
        </>

    )
}

export default PublicTasks