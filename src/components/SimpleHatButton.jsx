import { Children, useState } from "react"
import searchicon from "../assets/ICONS/SEARCH.svg"
import editicon from "../assets/ICONS/EDIT.svg"
import plusicon from "../assets/ICONS/PLUSWHITE.svg"
import supporticon from "../assets/ICONS/SUPPORT.svg"
import arbitrageicon from "../assets/ICONS/ARBITRAGE.svg"
import logout from "../assets/ICONS/OFF.svg"
import messageicon from "../assets/ICONS/MESSAGE.svg"
import ordersicon from "../assets/ICONS/ORDERS.svg"

export const SimpleHatButton = ({ icon, style, isActive, children, ...props }) => {
    const className = isActive == "true" ? 'hat-ui-button-black' : 'hat-ui-button';
    const icons = {
        messages: messageicon,
        notifications: null,
        wallet: null,
        logout: logout,
        search: searchicon,
        edit: editicon,
        plus: plusicon,
        support: supporticon,
        arbitrage: arbitrageicon,
        order: ordersicon
    };

    return (
        <button className={className} {...props}>
            {icon && icons[icon] ? (
                <img className="buttonicon" src={icons[icon]} />) : null
            }
            {children}
        </button>
    )
}

export default SimpleHatButton