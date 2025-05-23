import { X } from 'lucide-react';

export default function Modal({ title, children, onClose }) {
    return (
        <div
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={onClose}
        >
            <div
                className="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6"
                onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside modal
            >
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition"
                >
                    <X size={20} />
                </button>

                {/* Modal Title */}
                {title && (
                    <h3 className="text-xl font-semibold text-indigo-700 mb-4 text-center">
                        {title}
                    </h3>
                )}

                {/* Modal Body */}
                <div className="text-center text-gray-700">{children}</div>
            </div>
        </div>
    );
}
