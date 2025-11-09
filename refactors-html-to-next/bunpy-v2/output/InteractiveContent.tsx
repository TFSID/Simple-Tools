import React, { useState, useCallback } from 'react';

/**
 * Props for the InteractiveContent component.
 */
interface InteractiveContentProps {
  /**
   * Optional initial value for the counter. Defaults to 0.
   */
  initialCount?: number;
  /**
   * Optional maximum value the counter can reach.
   */
  maxCount?: number;
  /**
   * Optional minimum value the counter can reach.
   */
  minCount?: number;
}

/**
 * A basic interactive component demonstrating state management and user interaction.
 * It features a counter with increment, decrement, and reset functionality,
 * including basic error handling for count limits.
 */
const InteractiveContent: React.FC<InteractiveContentProps> = ({
  initialCount = 0,
  maxCount = Number.MAX_SAFE_INTEGER,
  minCount = Number.MIN_SAFE_INTEGER,
}) => {
  const [count, setCount] = useState<number>(initialCount);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles incrementing the counter.
   * Prevents incrementing beyond `maxCount`.
   */
  const handleIncrement = useCallback(() => {
    try {
      if (count >= maxCount) {
        throw new Error(`Count cannot exceed ${maxCount}.`);
      }
      setCount((prevCount) => prevCount + 1);
      setError(null); // Clear any previous error
    } catch (e: any) {
      setError(e.message || 'An unknown error occurred during increment.');
      console.error('Error incrementing count:', e);
    }
  }, [count, maxCount]);

  /**
   * Handles decrementing the counter.
   * Prevents decrementing below `minCount`.
   */
  const handleDecrement = useCallback(() => {
    try {
      if (count <= minCount) {
        throw new Error(`Count cannot go below ${minCount}.`);
      }
      setCount((prevCount) => prevCount - 1);
      setError(null); // Clear any previous error
    } catch (e: any) {
      setError(e.message || 'An unknown error occurred during decrement.');
      console.error('Error decrementing count:', e);
    }
  }, [count, minCount]);

  /**
   * Resets the counter to its initial value.
   */
  const handleReset = useCallback(() => {
    setCount(initialCount);
    setError(null); // Clear any error on reset
  }, [initialCount]);

  return (
    <div
      style={{
        padding: '20px',
        margin: '20px auto',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        maxWidth: '500px',
        textAlign: 'center',
        backgroundColor: '#ffffff',
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      <h2 style={{ color: '#333', marginBottom: '15px' }}>Interactive Counter</h2>
      <p style={{ fontSize: '1.5em', marginBottom: '20px', color: '#555' }}>
        Current Count: <strong style={{ color: '#007bff' }}>{count}</strong>
      </p>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '15px',
          marginBottom: '20px',
        }}
      >
        <button
          onClick={handleDecrement}
          disabled={count <= minCount} // Disable if at min limit
          style={{
            padding: '10px 20px',
            fontSize: '1em',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: count <= minCount ? 'not-allowed' : 'pointer',
            opacity: count <= minCount ? 0.6 : 1,
            transition: 'background-color 0.3s ease',
          }}
          aria-label="Decrement count"
        >
          Decrement
        </button>
        <button
          onClick={handleIncrement}
          disabled={count >= maxCount} // Disable if at max limit
          style={{
            padding: '10px 20px',
            fontSize: '1em',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: count >= maxCount ? 'not-allowed' : 'pointer',
            opacity: count >= maxCount ? 0.6 : 1,
            transition: 'background-color 0.3s ease',
          }}
          aria-label="Increment count"
        >
          Increment
        </button>
      </div>
      <button
        onClick={handleReset}
        disabled={count === initialCount && !error} // Disable if already at initial and no error
        style={{
          padding: '8px 15px',
          fontSize: '0.9em',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: (count === initialCount && !error) ? 'not-allowed' : 'pointer',
          opacity: (count === initialCount && !error) ? 0.6 : 1,
          transition: 'background-color 0.3s ease',
        }}
        aria-label="Reset count"
      >
        Reset
      </button>

      {error && (
        <p
          role="alert"
          style={{
            color: '#dc3545',
            marginTop: '20px',
            padding: '10px',
            border: '1px solid #dc3545',
            borderRadius: '5px',
            backgroundColor: '#ffe6e6',
            fontSize: '0.9em',
          }}
        >
          Error: {error}
        </p>
      )}
    </div>
  );
};

export default InteractiveContent;