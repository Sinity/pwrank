/**
 * Application-wide constants and configuration values.
 * These values should match backend constants where applicable.
 */

// Image fallback for broken or missing images
export const FALLBACK_IMAGE_SVG =
  'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2224%22%3ENo Image%3C/text%3E%3C/svg%3E';

// Password requirements (should match backend MIN_PASSWORD_LENGTH)
export const MIN_PASSWORD_LENGTH = 8;
export const MAX_PASSWORD_LENGTH = 128;

// Input length limits (should match backend validation)
export const MAX_ITEM_LABEL_LENGTH = 200;
export const MAX_IMAGE_URL_LENGTH = 500;
export const MAX_RANKING_NAME_LENGTH = 255;

// Rating scale (should match backend RATING_SCALE_MIN/MAX)
export const RATING_SCALE_MIN = 0;
export const RATING_SCALE_MAX = 10;
export const DEFAULT_INIT_RATING = 5;

// UI configuration
export const SEARCH_DEBOUNCE_MS = 300;
export const TOAST_DURATION_SHORT = 2000;
export const TOAST_DURATION_NORMAL = 3000;
export const TOAST_DURATION_LONG = 4000;

// Pagination
export const DEFAULT_ITEMS_PER_PAGE = 20;

// Minimum items required for comparison (should match backend MIN_ITEMS_FOR_RANKING)
export const MIN_ITEMS_FOR_RANKING = 2;
