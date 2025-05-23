import React, { useState } from 'react';
import Modal from '../components/Modal';
import { Loader2 } from 'lucide-react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function AdminPanel() {
  const [image, setImage] = useState(null);
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  const [previewUrl, setPreviewUrl] = useState(null);
  const [tags, setTags] = useState([]);

  const handleFileChange = (e) => {
    setTags([]); // reset tags on new file selection
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
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/upload_pose`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setTags(result.tags);
        setModalMessage('✅ Image uploaded successfully!');
      } else {
        setModalMessage(`❌ Oops! We couldn’t detect your pose in this photo. Please try uploading another one. Thanks a bunch!`);
      }
    } catch (error) {
      setModalMessage(`❌ Oops! We couldn’t detect your pose in this photo. Please try uploading another one. Thanks a bunch!`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-8 rounded-2xl space-y-6">
      <h2 className="text-3xl font-bold text-center text-indigo-700">📸 Admin Panel — Upload Poses</h2>

      {/* Location Input */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <input
          type="text"
          placeholder="Enter location (optional)"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="w-full sm:w-2/3 px-4 py-2 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-400 outline-none transition"
        />
      </div>

      {/* File Upload */}
      <div className="text-center">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold
                     file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200 transition cursor-pointer"
        />
      </div>

      {/* Preview */}
      {previewUrl && (
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Selected Image Preview:</h3>
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full sm:w-1/2 max-h-80 object-cover mx-auto rounded-xl shadow-md transform transition duration-300 hover:scale-105"
          />
        </div>
      )}

      {/* Upload Button */}
      <div className="text-center">
        <button
          onClick={handleUpload}
          disabled={!image}
          className={`px-6 py-2 rounded-full font-semibold text-white transition inline-flex items-center gap-2 ${image
            ? 'bg-green-500 hover:bg-green-600'
            : 'bg-green-300 cursor-not-allowed'
            }`}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Uploading...
            </>
          ) : (
            'Upload Image'
          )}
        </button>
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Tags:</h3>
          <div className="flex flex-wrap justify-center gap-2">
            {tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium shadow"
              >
                {`'${tag}'`}
              </span>
            ))}
          </div>
        </div>
      )}
      {/* Modal */}
      {modalMessage && (
        <Modal title="Upload Result" onClose={() => setModalMessage('')}>
          <p>{modalMessage}</p>
        </Modal>
      )}
    </div>
  );

}

export default AdminPanel;
