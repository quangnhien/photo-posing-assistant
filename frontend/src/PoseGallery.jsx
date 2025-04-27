import React from 'react';

const poses = [
  { id: 1, url: '/poses/pose1.jpg' },
  { id: 2, url: '/poses/pose2.jpg' },
  { id: 3, url: '/poses/pose3.jpg' },
  { id: 4, url: '/poses/pose4.jpg' },
];

function PoseGallery({ selectedPose, onSelectPose }) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">1️⃣ Choose a Pose</h2>

      {selectedPose ? (
        <div className="relative">
          <div className="overflow-hidden rounded-2xl shadow-md">
            <img 
              src={selectedPose.url} 
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
                src={pose.url} 
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
