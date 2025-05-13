import { useEffect, useState, useContext, useRef } from "react";
import { AuthContext } from '../../context/AuthContext.jsx';
import api from '../../services/api';
import { SERVER_URL } from "../../pathconfig.js";
import MiniProfile from "./MiniProfile.jsx";
import { Link } from "react-router-dom";
import SimpleButton from "../SimpleButton.jsx";
import SimpleHatButton from "../SimpleHatButton.jsx";

export const Feedback = ({ taskid }) => {
    const [feedbacks, setFeedbacks] = useState([]);

    const feedbacksFetcher = async () => {
        if (!taskid) return;
        try {
            const response = await api.get(`/tasks/tasks/${taskid}/applications`);
            const filteredFeedbacks = response.data.filter(feedback => feedback.status === "На рассмотрении");
            setFeedbacks(filteredFeedbacks);
        }
        catch (error) {
            console.log(error);
        }
    }

    useEffect(() => {
        feedbacksFetcher();
    }, [taskid])

    const feedbackAccept = async (id) => {
        if (!id) return;
        try {
            const response = await api.post(`/tasks/tasks/${taskid}/applications/${id}/accept`);
            console.log(response);
        }
        catch (error) {
            console.log(error);
        }
    }

    return (
        <>
            {feedbacks.map((feedback) => (
                <div key={feedback.id} className="bodyblock black">
                    <div className="bodyblock bodyblockwp black gap10 fxrow">
                        <Link to={`/profile/` + feedback.freelancer_id}><MiniProfile id={feedback.freelancer_id}></MiniProfile></Link>
                        <SimpleHatButton onClick={() => feedbackAccept(feedback.id)}>+</SimpleHatButton>
                        <SimpleHatButton>-</SimpleHatButton>
                    </div>
                </div>
            ))}
        </>
    )
}

export default Feedback