import React, { useState } from 'react';
import PoseGallery from './PoseGallery';
import UploadPhoto from './UploadPhoto';
import CompareForm from './CompareForm';
import Result from './Result';

function App() {
  const [selectedPose, setSelectedPose] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [instructionImage, setInstructionImage] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-purple-100 p-8">
      <div className="max-w-5xl mx-auto bg-white shadow-2xl rounded-3xl p-8 space-y-8">
        <h1 className="text-4xl font-bold text-center text-indigo-600 mb-8">🌎 Travel Pose Helper</h1>

        {/* Row with two columns */}

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
          onResult={setInstructionImage}
        />

        {instructionImage && <Result instructionImage={instructionImage} />}
      </div>
    </div>
  );
}

export default App;
