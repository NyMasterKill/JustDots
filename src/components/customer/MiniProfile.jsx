import { useEffect, useState } from "react";
import api from "../../services/api";
import { SERVER_URL } from "../../pathconfig";

export const MiniProfile = ({ id }) => {
    const [profile, setProfile] = useState({});

    const profileFetcher = async () => {
        if (!id) return;

        try {
            const response = await api.get(`/users/profile/${id}`);
            setProfile(response.data);
            console.log(`Профиль ${id} получен`);
        }
        catch (error) {
            console.log(error);
        }
    }

    useEffect(() => {
        profileFetcher();
    }, [id])

    if (!profile) return;
    return (
        <>
            <div className="miniprofile-white">
                {profile.username}
                <div className="miniprofile-avatar">
                    {profile.profile?.avatar_url ? (
                        <img src={SERVER_URL + (profile?.profile?.avatar_url)}></img>
                    ) : (
                        <div className="ellipse"> </div>
                    )}
                </div>
            </div>
        </>
    )
}

export default MiniProfile