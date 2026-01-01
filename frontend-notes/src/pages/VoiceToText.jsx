import React, { useEffect, useState, useRef } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";

const VoiceToText = () => {
  const [transcribing, setTranscribing] = useState(false);
  const [content, setContent] = useState("");
  const [bufferText, setBufferText] = useState("");
  const wsRef = useRef(null);
  const quillRef = useRef(null);
  const mediaRecorderRef = useRef(null);

  const token = localStorage.getItem("access_token");

  const startTranscription = async () => {
    if (transcribing) return;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    wsRef.current = new WebSocket(`ws://127.0.0.1:8000/voice/ws?token=${token}`);

    wsRef.current.onopen = () => {
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = async (e) => {
        if (e.data.size > 0 && wsRef.current.readyState === 1) {
          const arrayBuffer = await e.data.arrayBuffer();
          wsRef.current.send(arrayBuffer);
        }
      };

      recorder.start(300);
      setTranscribing(true);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (!data.text) return;

      setContent(prev => prev + " " + data.text);
    };

    wsRef.current.onclose = () => {
      setTranscribing(false);
    };

    wsRef.current.onerror = () => {
      toast.error("WebSocket error!");
      setTranscribing(false);
    };
  };

  const stopTranscription = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setTranscribing(false);
      setBufferText("");
    }
  };

  const moveCursorToEnd = () => {
    const editor = quillRef.current?.getEditor();
    if (editor) editor.setSelection(editor.getLength(), editor.getLength());
  };

  return (
    <div className="p-5">
      <ToastContainer position="top-right" autoClose={2000} />
      <h2 className="text-2xl mb-3">Live Voice to Text</h2>

      <div className="relative mb-4">
        <ReactQuill
          ref={quillRef}
          value={content}
          onChange={setContent}
          placeholder="Speak here..."
          className="border rounded-lg"
          style={{ minHeight: "200px" }}
        />
        <button
          onClick={transcribing ? stopTranscription : startTranscription}
          className={`absolute right-3 top-1 p-2 rounded-full text-white shadow-lg ${
            transcribing ? "bg-red-600" : "bg-green-600"
          }`}
        >
          {transcribing ? "🎤 Stop" : "🎙️ Start"}
        </button>
      </div>
    </div>
  );
};

export default VoiceToText;
