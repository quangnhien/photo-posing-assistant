import { Link } from 'react-router-dom';

export default function NavItem({ path, label, active, onClick }) {
    return (
        <Link
            to={path}
            onClick={onClick}
            className={`px-4 py-2 rounded-full font-medium transition duration-200
        ${active
                    ? 'bg-indigo-500 text-white'
                    : 'text-indigo-700 hover:bg-indigo-500 hover:text-white'}
      `}
        >
            {label}
        </Link>
    );
}