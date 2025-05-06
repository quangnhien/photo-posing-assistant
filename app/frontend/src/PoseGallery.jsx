import React, { useEffect, useState } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PoseGallery({ selectedPose, onSelectPose }) {
  const [poses, setPoses] = useState([]);
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [timeoutId, setTimeoutId] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Initial load of popular poses
  useEffect(() => {
    fetch(`${API_BASE_URL}/popular_poses`)
      .then(res => res.json())
      .then(data => setPoses(data.poses || []))
      .catch(err => console.error('Failed to load images', err));
  }, []);

  // Live search when query changes (with debounce)
  useEffect(() => {
    if (!query.trim()) return;

    if (timeoutId) clearTimeout(timeoutId); // clear previous timeout

    const id = setTimeout(async () => {
      fetch(`${API_BASE_URL}/search_poses?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => setPoses(data.poses || []))
        .catch(err => console.error('Failed to load images', err));
    }, 400); // 400ms debounce

    setTimeoutId(id);
  }, [query]);
  // Handle image search
  const handleImageSearch = async () => {
    if (!selectedImage && !query.trim()) return;

    const formData = new FormData();
    if (selectedImage) formData.append('image', selectedImage);
    if (query.trim()) formData.append('text', query.trim());

    setSearching(true);
    try {
      const res = await fetch(`${API_BASE_URL}/search_combined`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setPoses(data.results || []);
    } catch (err) {
      console.error('Combined search failed', err);
    } finally {
      setSearching(false);
    }
  };


  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">1️⃣ Choose a Pose</h2>

      {/* Search input and image upload */}
      {!selectedPose &&<div className="mb-4 flex flex-col sm:flex-row gap-2 items-center">
        {/* Keyword input (live search) */}
        <input
          type="text" 
          placeholder="Search by keyword..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        {/* Image upload input (hidden, stores file in state) */}
        <input
          type="file"
          accept="image/*"
          id="image-upload"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files[0];
            setSelectedImage(file);
            if (file) {
              setPreviewUrl(URL.createObjectURL(file));
            }
          }}

        />
        <label htmlFor="image-upload" className="cursor-pointer px-4 py-2 bg-indigo-100 border border-indigo-300 rounded-full text-indigo-700 font-medium text-sm hover:bg-indigo-200">
          📷 Choose Image
        </label>
        {previewUrl && (
          <div className="mt-2">
            <p className="text-sm text-gray-600 mb-1">Image for searching:</p>
            <img
              src={previewUrl}
              alt="Selected"
              className="w-40 h-[160px] object-cover rounded-xl border shadow-sm"
            />
          </div>
        )}

        {/* Search image button */}
        <button
          type="button"
          onClick={handleImageSearch}
          className="px-4 py-2 bg-indigo-500 text-white rounded-full font-semibold hover:bg-indigo-600 disabled:opacity-50"
          disabled={!selectedImage && !query.trim()}
        >
          🔍 Search by Text + Image
        </button>

      </div>}


      {(searching) && (
        <p className="text-sm text-gray-500 mb-2">{searching ? 'Searching by image...' : 'Searching by text...'}</p>
      )}

      {selectedPose ? (
        <div className="relative">
          <div className="overflow-hidden rounded-2xl shadow-md">
            <img
              src={selectedPose.image_url}
              alt="Selected Pose"
              className="w-full h-[480px] object-cover transform transition-transform duration-300 hover:scale-105"
            />
          </div>
          <button
            onClick={() => onSelectPose(null)}
            className="absolute top-4 right-4 bg-indigo-500 hover:bg-indigo-600 text-white py-2 px-4 rounded-full text-sm shadow-md transition"
          >
            🔄
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {poses.map(pose => (
            <div
              key={pose.id}
              onClick={() => onSelectPose(pose)}
              className="cursor-pointer overflow-hidden rounded-2xl shadow-md"
            >
              <img
                src={pose.image_url}
                alt={`Pose ${pose.id}`}
                className="w-full h-[320px] object-cover transform transition-transform duration-300 hover:scale-105"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PoseGallery;
