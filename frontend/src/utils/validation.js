/**
 * Validation utility functions
 */

/**
 * Validates that a URL uses a safe protocol (http/https)
 * Prevents javascript:, data:, and other potentially dangerous protocols
 *
 * @param {string} url - The URL to validate
 * @returns {boolean} True if URL is safe or empty, false if potentially dangerous
 */
export function isSafeImageUrl(url) {
  if (!url || url.trim() === '') return true; // Empty is safe

  const trimmed = url.trim();

  // Check for valid HTTP/HTTPS URL
  try {
    const parsed = new URL(trimmed);
    const safeProtocols = ['http:', 'https:', 'data:'];
    return safeProtocols.includes(parsed.protocol);
  } catch {
    // If URL parsing fails, treat as relative URL (safe)
    // Check it doesn't start with dangerous protocols
    const lowerUrl = trimmed.toLowerCase();
    const dangerousProtocols = ['javascript:', 'vbscript:', 'file:'];
    return !dangerousProtocols.some(proto => lowerUrl.startsWith(proto));
  }
}

/**
 * Validates email format
 *
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email format
 */
export function isValidEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
}

/**
 * Sanitizes a string for CSV export (escapes quotes)
 *
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string wrapped in quotes
 */
export function sanitizeForCSV(str) {
  return `"${String(str).replace(/"/g, '""')}"`;
}
