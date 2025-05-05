import React, { useState } from 'react';
import PoseGallery from './PoseGallery';
import UploadPhoto from './UploadPhoto';
import CompareForm from './CompareForm';
import FeedbackForm from './FeedbackForm';
import Result from './Result';
import AdminPanel from './AdminPanel'; // <- Create this component

function App() {
  const [view, setView] = useState('user'); // 'user' or 'admin'
  const [selectedPose, setSelectedPose] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-purple-100 p-8">
      <div className="max-w-5xl mx-auto bg-white shadow-2xl rounded-3xl p-8 space-y-8">

        {/* Header with buttons */}
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-4xl font-bold text-indigo-600">🌎 Travel Pose Helper</h1>
          <div className="space-x-4">
            <button
              className={`px-4 py-2 rounded-full font-semibold ${view === 'user' ? 'bg-indigo-500 text-white' : 'bg-gray-200'}`}
              onClick={() => setView('user')}
            >
              User
            </button>
            <button
              className={`px-4 py-2 rounded-full font-semibold ${view === 'admin' ? 'bg-indigo-500 text-white' : 'bg-gray-200'}`}
              onClick={() => setView('admin')}
            >
              Admin
            </button>
          </div>
        </div>

        {/* View rendering */}
        {view === 'user' ? (
          <>
            <div className="flex flex-wrap justify-between gap-8 items-start">
              <div className="flex-1 basis-[45%] flex flex-col justify-start">
                <PoseGallery selectedPose={selectedPose} onSelectPose={setSelectedPose} />
              </div>
              <div className="flex-1 basis-[45%] flex flex-col justify-start">
                <UploadPhoto uploadedImage={uploadedImage} onUpload={setUploadedImage} />
              </div>
            </div>

            <CompareForm
              selectedPose={selectedPose}
              uploadedImage={uploadedImage}
            />


          </>
        ) : (
          <AdminPanel />
        )}
      </div>
    </div>
  );
}

export default App;
