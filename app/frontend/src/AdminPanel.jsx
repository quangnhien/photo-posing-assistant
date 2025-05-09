import React, { useState } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function AdminPanel() {
  const [image, setImage] = useState(null);
  const [location, setLocation] = useState('');

  const [previewUrl, setPreviewUrl] = useState(null);
  const [tags, setTags] = useState([]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    if (file) {
      setPreviewUrl(URL.createObjectURL(file)); // create preview URL
    } else {
      setPreviewUrl(null);
    }
  };

  const handleUpload = async () => {
    if (!image) return;

    const formData = new FormData();
    formData.append('file', image);
    if (location.trim()) {
      formData.append('location', location.trim());
    }



    try {
      const response = await fetch(`${API_BASE_URL}/upload_pose`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setTags(result.tags); // Set the tags to show below
        alert('✅ Image uploaded successfully!');
      } else {
        console.error(`❌ Upload failed: ${result.error}`);
        alert(`❌ Oops! We couldn’t detect your pose in this photo. Please try uploading another one. Thanks a bunch!`);
      }
    } catch (error) {
      console.error('❌ Upload error:', error);
      alert(`❌ Oops! We couldn’t detect your pose in this photo. Please try uploading another one. Thanks a bunch!`);
    }
  };
  console.log(tags)
  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4 text-indigo-600">Admin Panel - Upload Poses</h2>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Enter location (optional)"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="border px-3 py-2 rounded w-1/3"
        />
      </div>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="mb-4"
      />

      {previewUrl && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Selected Image Preview:</h3>
          <img
            src={previewUrl}
            alt="Preview"
            className="w-1/3 mx-auto object-cover transform transition-transform duration-300 hover:scale-105"
          />
        </div>
      )}

      <button
        onClick={handleUpload}
        className="px-6 py-2 bg-green-500 text-white rounded-full font-semibold"
        disabled={!image}
      >
        Upload Image
      </button>

      {tags.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Tags:</h3>
          <div className="flex flex-wrap justify-center gap-2">
            {tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
              >
                {'\'' + tag + '\'' + ","}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;
