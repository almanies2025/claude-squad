"use client";

import { useRef, useEffect } from "react";

/**
 * VideoCityscape — Looping video backdrop.
 * Premium dark: 30-35% opacity, strong overlay so content pops.
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
          opacity: 0.32,
          filter: "saturate(0.6) brightness(0.65) contrast(1.05)",
        }}
      >
        {/* User-supplied backdrop video */}
        <source src="/videos/backdrop.mp4" type="video/mp4" />
      </video>

      {/* Strong dark overlay — content must remain fully readable */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, rgba(13,17,23,0.75) 0%, rgba(13,17,23,0.60) 35%, rgba(13,17,23,0.80) 100%)",
          zIndex: 1,
        }}
      />
    </div>
  );
}
