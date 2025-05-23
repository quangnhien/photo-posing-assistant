import React, { useState } from 'react';

function UploadPhoto({ uploadedImage, onUpload }) {
    const [previewUrl, setPreviewUrl] = useState(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            onUpload(file);
            setPreviewUrl(URL.createObjectURL(file));
        }
    };

    return (
        <div className="flex flex-col items-center justify-center sm:p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-4">2️⃣ Upload Your Photo</h2>

            {uploadedImage && (
                <div className="relative">
                    <div className="overflow-hidden rounded shadow-md">
                        <img
                            src={previewUrl}
                            alt="Uploaded"
                            className="w-full sm:h-[480px] object-cover transform transition-transform duration-300 hover:scale-105"
                        />
                    </div>


                </div>
            )}

            <div className="flex items-center justify-center">
                <label className="cursor-pointer bg-indigo-500 hover:bg-indigo-600 text-white py-3 px-6 rounded-full shadow-md">
                    Upload Image
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileChange}
                    />
                </label>
            </div>
        </div>
    );
}

export default UploadPhoto;
