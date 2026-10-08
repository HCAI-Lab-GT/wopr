import { useCallback, useEffect, useRef, useState } from 'react';

const DEFAULT_PLAYBACK_RATE_MS = 700;
const TEXT_INPUT_TYPES = new Set(['input', 'textarea', 'select']);

function isEditableTarget(target) {
  if (!target) return false;
  const tagName = target.tagName?.toLowerCase();
  if (TEXT_INPUT_TYPES.has(tagName)) return true;
  return target.isContentEditable === true;
}

export function useReplayPlayback({ enabled = true, frameIndex, frameCount, setFrameIndex, onSearchFocus, rateMs = DEFAULT_PLAYBACK_RATE_MS }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const rateRef = useRef(rateMs);

  useEffect(() => {
    rateRef.current = rateMs;
  }, [rateMs]);

  const play = useCallback(() => {
    if (!enabled || frameCount <= 1) return;
    setIsPlaying(true);
  }, [enabled, frameCount]);

  const pause = useCallback(() => setIsPlaying(false), []);

  const togglePlay = useCallback(() => {
    setIsPlaying((current) => {
      if (!enabled) return false;
      if (!current && frameCount <= 1) return false;
      return !current;
    });
  }, [enabled, frameCount]);

  const keyboardHandler = useCallback(
    (event) => {
      if (event.defaultPrevented) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      if (isEditableTarget(event.target)) return;

      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault();
          setFrameIndex(Math.max(0, frameIndex - 1));
          break;
        case 'ArrowRight':
          event.preventDefault();
          setFrameIndex(Math.min(frameCount - 1, frameIndex + 1));
          break;
        case 'Home':
          event.preventDefault();
          setFrameIndex(0);
          break;
        case 'End':
          event.preventDefault();
          setFrameIndex(frameCount - 1);
          break;
        case ' ':
          event.preventDefault();
          togglePlay();
          break;
        case '/':
          event.preventDefault();
          onSearchFocus?.();
          break;
        default:
          break;
      }
    },
    [frameIndex, frameCount, setFrameIndex, togglePlay, onSearchFocus],
  );

  useEffect(() => {
    if (!enabled) return undefined;
    window.addEventListener('keydown', keyboardHandler);
    return () => window.removeEventListener('keydown', keyboardHandler);
  }, [enabled, keyboardHandler]);

  useEffect(() => {
    if (!enabled || !isPlaying) return undefined;
    const intervalId = window.setInterval(() => {
      setFrameIndex((current) => {
        if (current >= frameCount - 1) {
          setIsPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, rateRef.current);
    return () => window.clearInterval(intervalId);
  }, [enabled, isPlaying, frameCount, setFrameIndex]);

  return { isPlaying, play, pause, togglePlay };
}

export { DEFAULT_PLAYBACK_RATE_MS };
