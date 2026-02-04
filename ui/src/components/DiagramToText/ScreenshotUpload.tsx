import React from 'react';

interface ScreenshotUploadProps {
    onUpload: (file: File) => Promise<void>;
}

const ScreenshotUpload: React.FC<ScreenshotUploadProps> = ({ onUpload }) => {

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            onUpload(selectedFile);
        }
    };

    return (
        <div>
            <input type="file" accept="image/*" onChange={handleFileChange} />
        </div>
    );
};

export default ScreenshotUpload;