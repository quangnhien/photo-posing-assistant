import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import NavItem from './NavItem';
import PoseAILogo from '../assets/images/pose_ai.png';

export default function Header() {
    const [menuOpen, setMenuOpen] = useState(false);
    const location = useLocation();

    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/admin', label: 'Upload Image' },
    ];

    return (
        <header className="relative z-50 bg-white/60 backdrop-blur-md shadow-md px-4 sm:px-6 md:px-32 py-4">
            <div className="flex items-center justify-between">
                {/* Logo + Title */}
                <Link to="/" className="flex items-center gap-4">
                    <img className="w-10 sm:w-16 h-auto object-contain rounded-xl" src={PoseAILogo} alt="Pose AI Logo" />
                    <span className="text-xl sm:text-2xl font-extrabold text-indigo-700">Travel Pose Helper</span>
                </Link>

                {/* Mobile Toggle */}
                <div className="md:hidden">
                    <button
                        onClick={() => setMenuOpen(!menuOpen)}
                        aria-label="Toggle menu"
                        className="text-indigo-700"
                    >
                        {menuOpen ? <X size={28} /> : <Menu size={28} />}
                    </button>
                </div>

                {/* Desktop Nav */}
                <nav className="hidden md:flex gap-6">
                    {navLinks.map(link => (
                        <NavItem key={link.path} {...link} active={location.pathname === link.path} />
                    ))}
                </nav>
            </div>

            {/* Mobile Dropdown */}
            {menuOpen && (
                <nav className="md:hidden bg-white/90 px-6 pb-4 pt-2 space-y-2 rounded-b-2xl shadow-lg absolute left-0 right-0">
                    {navLinks.map(link => (
                        <NavItem
                            key={link.path}
                            {...link}
                            active={location.pathname === link.path}
                            onClick={() => setMenuOpen(false)}
                        />
                    ))}
                </nav>
            )}
        </header>
    );
}
