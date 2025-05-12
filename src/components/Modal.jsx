export const Modal = ({ children }) => {
    return (
        <div className="modal-background">
            <div className="styledblock">
                {children}
            </div>
        </div>
    )
}

export default Modal