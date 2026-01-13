import {create} from 'zustand';
import {User} from '../types';
import * as api from '../services/api';
import * as keychain from '../services/keychain';
import * as cache from '../services/cache';
import * as syncManager from '../services/syncManager';

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  user: null,
  isLoading: false,
  error: null,

  /**
   * Login with username and password
   */
  login: async (username: string, password: string) => {
    set({isLoading: true, error: null});

    try {
      const result = await api.login(username, password);

      if (result.success && result.token && result.user) {
        // Store token in Keychain
        await keychain.storeToken(result.token);

        // Update state
        set({
          token: result.token,
          user: result.user,
          isLoading: false,
          error: null,
        });

        // Start auto-sync
        syncManager.startAutoSync();
      } else {
        // Login failed
        set({
          isLoading: false,
          error: result.error || 'Login failed',
        });
      }
    } catch (error: any) {
      console.error('Login error:', error);
      set({
        isLoading: false,
        error: error.message || 'Login failed. Please try again.',
      });
    }
  },

  /**
   * Logout and clear all data
   */
  logout: async () => {
    try {
      // Clear token from Keychain
      await keychain.clearToken();

      // Clear all cached data
      cache.clear();

      // Clear sync queue
      await syncManager.clearQueue();

      // Stop auto-sync
      syncManager.stopAutoSync();

      // Reset state
      set({
        token: null,
        user: null,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      console.error('Logout error:', error);
      // Force reset state even if cleanup fails
      set({
        token: null,
        user: null,
        isLoading: false,
        error: null,
      });
    }
  },

  /**
   * Check if user is authenticated (on app launch)
   */
  checkAuth: async () => {
    set({isLoading: true});

    try {
      // Check for stored token
      const token = await keychain.getToken();

      if (token) {
        // Token exists, fetch user data
        const user = await api.getCurrentUser();

        set({
          token,
          user,
          isLoading: false,
          error: null,
        });

        // Start auto-sync
        syncManager.startAutoSync();
      } else {
        // No token, user not authenticated
        set({
          token: null,
          user: null,
          isLoading: false,
          error: null,
        });
      }
    } catch (error: any) {
      console.error('Check auth error:', error);

      // Token invalid or expired, clear it
      await keychain.clearToken();

      set({
        token: null,
        user: null,
        isLoading: false,
        error: null,
      });
    }
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({error: null});
  },
}));
