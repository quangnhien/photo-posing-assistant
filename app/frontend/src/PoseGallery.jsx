import React, { useEffect, useState } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PoseGallery({ selectedPose, onSelectPose }) {
  const [poses, setPoses] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/popular_poses`)
      .then(res => res.json())
      .then(data => setPoses(data.poses || []))
      .catch(err => console.error('Failed to load images', err));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">1️⃣ Choose a Pose</h2>
  
      {selectedPose ? (
        <div className="relative">
          <div className="overflow-hidden rounded-2xl shadow-md">
            <img 
              src={selectedPose.image_url} 
              alt="Selected Pose" 
              className="w-full h-80 object-cover transform transition-transform duration-300 hover:scale-105"
            />
          </div>
  
          {/* Floating Change button */}
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
                className="w-full h-40 object-cover transform transition-transform duration-300 hover:scale-105"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
  }
  

export default PoseGallery;

