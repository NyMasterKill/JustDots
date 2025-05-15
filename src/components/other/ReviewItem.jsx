import React, {useEffect, useState} from 'react';
import AutoTextarea from "./AutoTextarea.jsx";
import Icon from "./Icon.jsx";
import api from "../../services/api.jsx";
import {SERVER_URL} from "../../pathconfig.js";


const ReviewItem = ({item}) => {
    const [author, setAuthor] = useState({});

    useEffect(() => {
        const fetchAuthor = async () => {
            if(!item) return;
            try{
                const response = await api.get(`/users/profile/${item.user_id}`);
                setAuthor(response.data);
            }
            catch(error){
                console.log(error);
            }
        };

        fetchAuthor();
    }, [item]);

    if(!item) return;
    if(!author) return;
    console.log(author);
    return (
        <div className="bfxrow">
            <div className="message-container">
                <div className="message-author-avatar">
                    <div className="message-avatar-container">
                        {author?.profile?.avatar_url && (
                            <img style={{height: "100" + "%"}} src={SERVER_URL + author?.profile?.avatar_url}/>
                        )}
                    </div>
                </div>
                <div className="message-data">
                    <div className="message-author-name">
                        {author.username}
                    </div>
                    <div className="message-text">
                        {item.comment}
                    </div>
                </div>
                <div style={{marginLeft: 15 + "px"}} className="propblock black">
                    <Icon icon="star" color="gold"></Icon>
                    {item.score}
                </div>
            </div>
        </div>
    );
};

export default ReviewItem;