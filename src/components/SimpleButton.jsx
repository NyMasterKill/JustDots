import SearchIcon from "../assets/ICONS/SEARCH.svg?react"
import EditIcon from "../assets/ICONS/EDIT.svg?react"
import PlusIcon from "../assets/ICONS/PLUSWHITE.svg?react"
import SupportIcon from "../assets/ICONS/SUPPORT.svg?react"
import ArbitrageIcon from "../assets/ICONS/ARBITRAGE.svg?react"
import BackcIcon from "../assets/ICONS/BACKCIRCLE.svg?react"
import CheckIcon from "../assets/ICONS/INSPECT.svg?react"
import OrdersIcon from "../assets/ICONS/ORDERS.svg?react"

export const SimpleButton = ({ icon, iconColor, style, children, ...props }) => {
    const className = style ? `simple-button-${style}` : 'simple-button-white';
    const icons = {
        search: SearchIcon,
        edit: EditIcon,
        plus: PlusIcon,
        support: SupportIcon,
        arbitrage: ArbitrageIcon,
        backc: BackcIcon,
        check: CheckIcon,
        order: OrdersIcon,
    }

    const IconComponent = icon ? icons[icon] : null;

    return (
        <button className={className} {...props}>
            {IconComponent && (
                <IconComponent
                    className="buttonicon"
                    style={{
                        fill: iconColor || 'currentColor',
                        width: '1.2em',
                        height: '1.2em'
                    }}
                />
            )}
            {children}
        </button>
    )
}


export default SimpleButton