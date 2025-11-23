/**
 * Application-wide constants and configuration values.
 * These values should match backend constants where applicable to ensure
 * consistent validation and behavior across frontend and backend.
 *
 * @module constants
 */

/**
 * Data URI for fallback image SVG shown when images fail to load.
 * Displays a gray placeholder with "No Image" text.
 * @type {string}
 * @constant
 */
export const FALLBACK_IMAGE_SVG =
  'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2224%22%3ENo Image%3C/text%3E%3C/svg%3E';

/**
 * Minimum password length required for user registration.
 * Must match backend MIN_PASSWORD_LENGTH constant.
 * @type {number}
 * @constant
 * @default 8
 */
export const MIN_PASSWORD_LENGTH = 8;

/**
 * Maximum password length allowed for security and database constraints.
 * Must match backend MAX_PASSWORD_LENGTH constant.
 * @type {number}
 * @constant
 * @default 128
 */
export const MAX_PASSWORD_LENGTH = 128;

/**
 * Maximum length for item labels.
 * Must match backend validation.
 * @type {number}
 * @constant
 * @default 200
 */
export const MAX_ITEM_LABEL_LENGTH = 200;

/**
 * Maximum length for image URLs.
 * Must match backend validation.
 * @type {number}
 * @constant
 * @default 500
 */
export const MAX_IMAGE_URL_LENGTH = 500;

/**
 * Maximum length for ranking names.
 * Must match backend validation.
 * @type {number}
 * @constant
 * @default 255
 */
export const MAX_RANKING_NAME_LENGTH = 255;

/**
 * Minimum value on the rating scale.
 * Must match backend RATING_SCALE_MIN.
 * @type {number}
 * @constant
 * @default 0
 */
export const RATING_SCALE_MIN = 0;

/**
 * Maximum value on the rating scale.
 * Must match backend RATING_SCALE_MAX.
 * @type {number}
 * @constant
 * @default 10
 */
export const RATING_SCALE_MAX = 10;

/**
 * Default initial rating for new items before comparisons.
 * Represents the middle of the rating scale.
 * @type {number}
 * @constant
 * @default 5
 */
export const DEFAULT_INIT_RATING = 5;

/**
 * Debounce delay in milliseconds for search inputs.
 * Prevents excessive API calls while user is typing.
 * @type {number}
 * @constant
 * @default 300
 */
export const SEARCH_DEBOUNCE_MS = 300;

/**
 * Toast notification duration for quick success messages (2 seconds).
 * @type {number}
 * @constant
 * @default 2000
 */
export const TOAST_DURATION_SHORT = 2000;

/**
 * Toast notification duration for standard messages (3 seconds).
 * @type {number}
 * @constant
 * @default 3000
 */
export const TOAST_DURATION_NORMAL = 3000;

/**
 * Toast notification duration for important/error messages (4 seconds).
 * @type {number}
 * @constant
 * @default 4000
 */
export const TOAST_DURATION_LONG = 4000;

/**
 * Default number of items shown per page in paginated tables.
 * @type {number}
 * @constant
 * @default 20
 */
export const DEFAULT_ITEMS_PER_PAGE = 20;

/**
 * Minimum items required to perform pairwise ranking comparisons.
 * Must match backend MIN_ITEMS_FOR_RANKING for Bradley-Terry model.
 * @type {number}
 * @constant
 * @default 2
 */
export const MIN_ITEMS_FOR_RANKING = 2;
