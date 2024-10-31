import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

const Form = () => {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [selfie, setSelfie] = useState(null);
  const [video, setVideo] = useState(null);
  const [aadharImage, setAadharImage] = useState(null);
  const [panImage, setPanImage] = useState(null);
  const [recording, setRecording] = useState(false);

  const captureSelfie = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setSelfie(imageSrc);
  };

  const handleImageChange = (event, setImage) => {
    const file = event.target.files[0];
    if (file) {
      setImage(file);
    }
  };

  const startRecording = () => {
    setRecording(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: "video/webm",
    });
    let chunks = [];

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    };

    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      setVideo(blob);
      chunks = [];
    };

    mediaRecorderRef.current.start();

    setTimeout(() => {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }, 5000); // Stop recording after 5 seconds
  };

  const uploadData = async () => {
    if (!selfie || !video || !aadharImage || !panImage) return alert("Please provide selfie, video, Aadhaar, and PAN images.");

    const formData = new FormData();
    formData.append("aadhar", aadharImage, "aadhar.png");
    formData.append("pan", panImage, "pan.png");
    formData.append("selfie", dataURItoBlob(selfie), "selfie.png");
    formData.append("video", video, "video.webm");

    try {
      const response = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("Files uploaded successfully!");
        checkFaceMatch();
      } else {
        alert("Upload failed.");
      }
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("Error uploading files.");
    }
  };

  const dataURItoBlob = (dataURI) => {
    const byteString = atob(dataURI.split(",")[1]);
    const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
  };

  const checkFaceMatch = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/match", {
        method: "POST",
      });
      const result = await response.json();
      alert(result.message);  // Show "Face match found!" or "Face does not match."
    } catch (error) {
      console.error("Error matching faces:", error);
    }
  };  

  return (
    <div style={styles.container}>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/png"
        style={styles.webcam}
      />
      <button onClick={captureSelfie} style={styles.button}>
        Capture Selfie
      </button>
      <button onClick={startRecording} disabled={recording} style={styles.button}>
        {recording ? "Recording..." : "Start Recording Video"}
      </button>

      <div style={styles.fileUploadContainer}>
        <label style={styles.label}>Upload Aadhaar Image:</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageChange(e, setAadharImage)}
          style={styles.fileInput}
        />
        <label style={styles.label}>Upload PAN Image:</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageChange(e, setPanImage)}
          style={styles.fileInput}
        />
      </div>

      <button onClick={uploadData} style={styles.button}>
        Upload
      </button>

      {selfie && (
        <div style={styles.previewContainer}>
          <h4>Selfie Preview</h4>
          <img src={selfie} alt="Selfie" style={styles.previewImage} />
        </div>
      )}

      {video && (
        <div style={styles.previewContainer}>
          <h4>Video Preview</h4>
          <video src={URL.createObjectURL(video)} controls style={styles.previewVideo} />
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    backgroundColor: "#f0f0f0",
    padding: "20px",
  },
  webcam: {
    width: "200px",
    height: "150px",
    borderRadius: "8px",
  },
  button: {
    margin: "10px",
    padding: "8px 16px",
    fontSize: "14px",
    cursor: "pointer",
    borderRadius: "4px",
    border: "none",
    backgroundColor: "#007bff",
    color: "#fff",
  },
  fileUploadContainer: {
    marginTop: "20px",
    textAlign: "center",
  },
  label: {
    display: "block",
    marginBottom: "10px",
    fontWeight: "bold",
  },
  fileInput: {
    marginBottom: "20px",
  },
  previewContainer: {
    marginTop: "20px",
    textAlign: "center",
  },
  previewImage: {
    width: "200px",
    height: "auto",
    borderRadius: "8px",
    marginTop: "10px",
  },
  previewVideo: {
    width: "200px",
    height: "auto",
    borderRadius: "8px",
    marginTop: "9px",
  },
};

export default Form;
