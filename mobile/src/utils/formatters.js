/**
 * Utility functions for formatting dates, times, and durations
 */

/**
 * Format sport name to title case and remove underscores/hyphens
 * @param {string} sport - Sport name (e.g., 'table_tennis', 'squash')
 * @returns {string} Formatted sport name (e.g., 'Table Tennis', 'Squash')
 */
export const formatSportName = (sport) => {
  if (!sport) return '';

  // Remove underscores and hyphens, split into words
  const words = sport.replace(/[_-]/g, ' ').split(' ');

  // Capitalize first letter of each word
  return words
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Format a date string to a readable format
 * @param {string} dateString - ISO date string
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, options = {}) => {
  const date = new Date(dateString);
  const defaultOptions = {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  };
  return date.toLocaleDateString('en-US', defaultOptions);
};

/**
 * Format a detailed date with full information
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDetailedDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Calculate and format session duration
 * @param {string} startTime - ISO start time
 * @param {string} endTime - ISO end time (optional)
 * @returns {string} Formatted duration string
 */
export const getSessionDuration = (startTime, endTime) => {
  if (!endTime) return 'In progress';

  const start = new Date(startTime);
  const end = new Date(endTime);
  const durationMs = end - start;
  const minutes = Math.floor(durationMs / 60000);

  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
};

/**
 * Get detailed duration text
 * @param {string} startTime - ISO start time
 * @param {string} endTime - ISO end time (optional)
 * @returns {string} Formatted duration string
 */
export const getDetailedDuration = (startTime, endTime) => {
  if (!endTime) return 'In progress';

  const start = new Date(startTime);
  const end = new Date(endTime);
  const durationMs = end - start;
  const minutes = Math.floor(durationMs / 60000);

  if (minutes < 60) {
    return `${minutes} minutes`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
};

/**
 * Format time in seconds to MM:SS or HH:MM:SS
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time string
 */
export const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`;
};
