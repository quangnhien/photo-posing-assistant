import { Outlet } from 'react-router-dom';
import Header from './Header';

function Layout() {

    return (
        <>
            {/* Header */}
            <Header />

            {/* Content */}
            <div className="min-h-screen px-6 sm:px-32">
                <div className="py-8 sm:py-10 space-y-8">

                    <main className="min-h-[400px]">
                        <div className="bg-gradient-to-r from-blue-100 to-purple-100 shadow-2xl rounded-3xl p-8 space-y-8">
                            <Outlet />
                        </div>
                    </main>
                </div>
            </div>

            <footer className="text-center text-sm text-gray-600 pt-6 py-6">
                &copy; {new Date().getFullYear()} Travel Pose Helper — All rights reserved.
            </footer>
        </>
    );
}

export default Layout;
