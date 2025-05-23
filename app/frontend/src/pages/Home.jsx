import { useState } from "react";
import PoseGallery from "../components/PoseGallery";
import UploadPhoto from "../components/UploadPhoto";
import CompareForm from "../components/CompareForm";

export default function Home() {
    const [selectedPose, setSelectedPose] = useState(null);
    const [uploadedImage, setUploadedImage] = useState(null);

    return (
        <>
            {/* View rendering */}
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
    );
}