"use client";

import { useRef, useEffect } from "react";

/**
 * VideoCityscape — Looping video backdrop.
 * Falls back gracefully if the video can't load.
 */
export default function VideoCityscape() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    video.playbackRate = 0.85;
    video.play().catch(() => {});
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      <video
        ref={videoRef}
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.55,
          filter: "saturate(0.7) brightness(0.75) contrast(1.1)",
        }}
      >
        {/* User-supplied backdrop video */}
        <source src="/videos/backdrop.mp4" type="video/mp4" />
      </video>

      {/* Dark overlay to ensure content remains readable */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, rgba(3,2,12,0.55) 0%, rgba(3,2,12,0.3) 40%, rgba(3,2,12,0.65) 100%)",
          zIndex: 1,
        }}
      />
    </div>
  );
}
