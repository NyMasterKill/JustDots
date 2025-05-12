import littlelogo from "../assets/justdots_littlelogo.svg";
import defaultlogo from "../assets/justdots_logo.svg";
import SimpleButton from "./SimpleButton";

export const LogoContainer = ({ size }) => {
    return (
        <div className="logo-container">
            <img
                alt="justdots logo"
                src={size == "little" ? littlelogo : defaultlogo}
            />
        </div>
    );
};

export default LogoContainer