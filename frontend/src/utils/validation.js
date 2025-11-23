/**
 * Validation utility functions for form inputs and user data.
 * Provides consistent validation patterns across the application
 * with security-first approach.
 *
 * @module utils/validation
 */

/**
 * Validates that a URL uses a safe protocol to prevent XSS attacks.
 * Allows http://, https://, and data: URIs while blocking dangerous protocols
 * like javascript:, vbscript:, and file:.
 *
 * @example
 * ```js
 * isSafeImageUrl('https://example.com/image.jpg'); // true
 * isSafeImageUrl('javascript:alert(1)'); // false
 * isSafeImageUrl('data:image/png;base64,...'); // true
 * isSafeImageUrl(''); // true (empty is safe)
 * ```
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
 * Validates email format using a simple regex pattern.
 * Checks for basic email structure (local@domain.tld).
 *
 * @example
 * ```js
 * isValidEmail('user@example.com'); // true
 * isValidEmail('invalid.email'); // false
 * isValidEmail('user@domain'); // false (no TLD)
 * ```
 *
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid email format
 */
export function isValidEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
}

/**
 * Sanitizes a string for CSV export by escaping quotes and wrapping in quotes.
 * Follows RFC 4180 CSV standard for proper escaping.
 *
 * @example
 * ```js
 * sanitizeForCSV('Hello World'); // "Hello World"
 * sanitizeForCSV('Say "Hello"'); // "Say ""Hello"""
 * sanitizeForCSV('Value, with comma'); // "Value, with comma"
 * ```
 *
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string wrapped in quotes
 */
export function sanitizeForCSV(str) {
  return `"${String(str).replace(/"/g, '""')}"`;
}
