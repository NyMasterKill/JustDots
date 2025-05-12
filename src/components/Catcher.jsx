import errorsvg from "../assets/error.svg"
export const Catcher = ({ text }) => {

    return (
        <div className="catcher-box">
            <img src={errorsvg} alt="error" />
            {text}
        </div>
    );
};

export default Catcher