// frontend/src/TestConnection.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function TestConnection() {
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Call the Flask backend on component mount
        axios.get('http://localhost:5000/test')
            .then(response => {
                setMessage(response.data.message);
            })
            .catch(error => {
                setMessage("Error connecting to backend.");
                console.error("Error:", error);
            });
    }, []);

    return (
        <div>
            <h2>Backend Connection Test</h2>
            <p>{message}</p>
        </div>
    );
}

export default TestConnection;
