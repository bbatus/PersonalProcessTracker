import * as Keychain from 'react-native-keychain';
import {KEYCHAIN_SERVICE} from '../config';

/**
 * Store authentication token securely in iOS Keychain
 */
export const storeToken = async (token: string): Promise<void> => {
  try {
    await Keychain.setGenericPassword('auth_token', token, {
      service: KEYCHAIN_SERVICE,
    });
  } catch (error) {
    console.error('Failed to store token in Keychain:', error);
    throw new Error('Failed to store authentication token');
  }
};

/**
 * Retrieve authentication token from iOS Keychain
 */
export const getToken = async (): Promise<string | null> => {
  try {
    const credentials = await Keychain.getGenericPassword({
      service: KEYCHAIN_SERVICE,
    });

    if (credentials) {
      return credentials.password;
    }

    return null;
  } catch (error) {
    console.error('Failed to retrieve token from Keychain:', error);
    return null;
  }
};

/**
 * Clear authentication token from iOS Keychain
 */
export const clearToken = async (): Promise<void> => {
  try {
    await Keychain.resetGenericPassword({
      service: KEYCHAIN_SERVICE,
    });
  } catch (error) {
    console.error('Failed to clear token from Keychain:', error);
    throw new Error('Failed to clear authentication token');
  }
};

/**
 * Check if authentication token exists in Keychain
 */
export const hasToken = async (): Promise<boolean> => {
  const token = await getToken();
  return token !== null;
};
