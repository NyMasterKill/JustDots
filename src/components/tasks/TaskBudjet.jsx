import React from 'react';
import rubleicon from "../../assets/ICONS/RUBLE.svg";

const TaskBudjet = ({bmin, bmax, view}) => {
    return (
        <div className={view == "min" ? "taskblock-price" : "propblock taskblock-price"}>
        {bmax !== bmin ? (
            <>
                {bmin} - {bmax}
                < img style={{ height: 22 + "px" }} src={rubleicon}></img>
                <span style={{ fontSize: 17 + "px", paddingTop: 5 + "px" }}>за заказ</span>
            </>
        ) : (
            <>
                {bmax}
                < img style={{ height: 22 + "px" }} src={rubleicon}></img>
                <span style={{ fontSize: 17 + "px", paddingTop: 5 + "px" }}>за заказ</span>
            </>
        )}
        </div>
    );
};

export default TaskBudjet;