import { useEffect, useRef } from 'react';

export const usePolling = (callback, interval, enabled = true) => {
  const savedCallback = useRef();

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    if (!enabled) return;

    const tick = () => {
      savedCallback.current();
    };

    // Call immediately
    tick();

    // Then set up interval
    const id = setInterval(tick, interval);
    return () => clearInterval(id);
  }, [interval, enabled]);
};

export default usePolling;
