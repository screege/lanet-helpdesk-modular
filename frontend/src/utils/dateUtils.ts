/**
 * Date formatting utilities for LANET Helpdesk V3
 * Handles Mexico City timezone and Spanish locale formatting
 */

// Mexico City timezone
const MEXICO_TIMEZONE = 'America/Mexico_City';
const SPANISH_LOCALE = 'es-MX';

/**
 * Format date for display in Mexico City timezone with Spanish locale
 * Handles dates that are already in Mexico timezone correctly
 */
export const formatDateTime = (dateString: string | Date): string => {
  try {
    // If it's a string with timezone info (-06:00), extract the parts directly
    if (typeof dateString === 'string' && dateString.includes('-06:00')) {
      const timePart = dateString.split('T')[1].split('-')[0]; // Gets '21:58:59.915679'
      const datePart = dateString.split('T')[0]; // Gets '2025-07-09'

      // Format as DD/MM/YYYY, HH:MM:SS
      const formattedDate = datePart.split('-').reverse().join('/');
      const formattedTime = timePart.substring(0, 8); // Remove microseconds

      return `${formattedDate}, ${formattedTime}`;
    } else {
      // For other dates, use standard JavaScript Date handling
      const date = typeof dateString === 'string' ? new Date(dateString) : dateString;

      return date.toLocaleString(SPANISH_LOCALE, {
        timeZone: MEXICO_TIMEZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    }
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Fecha inválida';
  }
};

/**
 * Format date only (without time) in Mexico City timezone
 */
export const formatDate = (dateString: string | Date): string => {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    
    return date.toLocaleDateString(SPANISH_LOCALE, {
      timeZone: MEXICO_TIMEZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Fecha inválida';
  }
};

/**
 * Format time only in Mexico City timezone
 */
export const formatTime = (dateString: string | Date): string => {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    
    return date.toLocaleTimeString(SPANISH_LOCALE, {
      timeZone: MEXICO_TIMEZONE,
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Hora inválida';
  }
};

/**
 * Format date with long month name for detailed displays
 */
export const formatDateLong = (dateString: string | Date): string => {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    
    return date.toLocaleDateString(SPANISH_LOCALE, {
      timeZone: MEXICO_TIMEZONE,
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Fecha inválida';
  }
};

/**
 * Get current Mexico City time
 */
export const getCurrentMexicoTime = (): Date => {
  return new Date(new Date().toLocaleString("en-US", { timeZone: MEXICO_TIMEZONE }));
};

/**
 * Check if a date is today in Mexico City timezone
 */
export const isToday = (dateString: string | Date): boolean => {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    const today = getCurrentMexicoTime();
    
    const dateInMexico = new Date(date.toLocaleString("en-US", { timeZone: MEXICO_TIMEZONE }));
    
    return dateInMexico.toDateString() === today.toDateString();
  } catch (error) {
    return false;
  }
};
