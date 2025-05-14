import { Task } from "./tasks/Task.jsx"
import {useState, useEffect, useContext} from "react";
import api from "../services/api";
import SimpleButton from "./SimpleButton";
import {Link, useNavigate} from "react-router-dom";
import {AuthContext} from "../context/AuthContext.jsx";

export const MyTasks = () => {
    const {myuser} = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const route = myuser.user_type === "freelancer" ? "/tasks/tasks/in-progress-tasks" : myuser.user_type === "customer" ? "/tasks/tasks" : null;
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTasks = async () => {
            if (route == null) return;
            try {
                const response = await api.get(route);
                setTasks(response.data);
                setLoading(false);
            } catch (err) {
                {err.code == "ERR_BAD_REQUEST" && navigate("/login")};
                console.log(err);
            } finally {
                setLoading(false);
            }
        };

        fetchTasks();
    }, [myuser]);

    if (loading) {
        return (
            <>
                <div className="hatsaver"></div>
                <div className="blocktitle">загрузка заказов...</div>
            </>
        )
    }

    if (tasks.length === 0) {
        return (
            <>
                <div className="hatsaver"></div>
                <div className="blocktitle">мои заказы</div>
                {myuser.user_type === "customer" ? (
                    <>
                    <div>Вы ещё не создавали заказы</div>
                    <Link style={{textDecoration: "none"}} to="/create">
                        <SimpleButton style="black" icon="plus">Создать заказ</SimpleButton>
                    </Link>
                    </>
                ) : (
                    <>
                    <div>У вас нету активных заказов</div>
                    <Link style={{textDecoration: "none"}} to="/orders">
                    <SimpleButton style="white" icon="search">Лента заказов</SimpleButton>
                    </Link>
                    </>
                    )}

            </>
        )
    }

    return (
        <>
            <div className="hatsaver"></div>
            <div className="blocktitle">мои заказы</div>
            <div className="bodyblock gap10">
                {tasks.map((task) => (
                    <Task key={task.id} task={task} />
                ))}
            </div>
        </>

    )
}

export default MyTasks