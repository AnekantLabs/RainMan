/**
 * Mock account data for testing
 * This will be replaced by actual API endpoints when the backend is ready
 */

// Mock accounts data
const mockAccountsData = [
  {
    id: "1",
    account_name: "Main Account",
    role: "main",
    api_key: "ky2pMdTFvbnmzYBYZZ",
    api_secret: "s2u8FthGmzpDqWGBcNL2JPZC",
    risk_percentage: "5",
    leverage: "10",
    is_activate: true,
    created_at: "2025-01-15 10:22:33",
    last_updated: "2025-02-25 15:30:42",
  },
  {
    id: "2",
    account_name: "Sub Account 1",
    role: "sub",
    api_key: "7LZwCxz8TFMpRrJk4m",
    api_secret: "Vn5xYzMp9LkJhGtRqWsPzK2F",
    risk_percentage: "3",
    leverage: "5",
    is_activate: true,
    created_at: "2025-01-20 13:45:22",
    last_updated: "2025-02-15 09:11:03",
  },
  {
    id: "3",
    account_name: "Sub Account 2",
    role: "sub",
    api_key: "Bu3nXs5YmWcTvNrKqL",
    api_secret: "pK8zDw2YvFrGhB3sQxTnM5J7",
    risk_percentage: "7",
    leverage: "20",
    is_activate: true,
    created_at: "2025-01-25 08:14:53",
    last_updated: "2025-02-10 18:32:15",
  },
  {
    id: "4",
    account_name: "Sub Account 3",
    role: "sub",
    api_key: "TkLpZx2MvN4rBsDq3Y",
    api_secret: "A7bNm6Y3zXcVfRgT5pH2sK9L",
    risk_percentage: "2",
    leverage: "3",
    is_activate: true,
    created_at: "2025-01-30 11:09:41",
    last_updated: "2025-02-20 14:25:37",
  },
  {
    id: "5",
    account_name: "Sub Account 4",
    role: "sub",
    api_key: "J8pQrS4tMbNv3zXcK",
    api_secret: "F9hJkL2mNbVcX3Zs7tR5p6Y4",
    risk_percentage: "4",
    leverage: "8",
    is_activate: false,
    created_at: "2025-02-05 16:27:33",
    last_updated: "2025-02-22 10:05:12",
  },
];

// Mock account metrics data
const mockAccountMetricsData = {
  1: { balance: "$14,000", performance: 60 },
  2: { balance: "$3,000", performance: 10 },
  3: { balance: "Not set", performance: 100 },
  4: { balance: "$20,500", performance: 100 },
  5: { balance: "$500", performance: 25 },
};

/**
 * Mock API functions for accounts
 */
const AccountsAPI = {
  /**
   * Get all accounts
   * @returns {Promise<Array>} - Promise resolving to an array of accounts
   */
  getAllAccounts: () => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        resolve([...mockAccountsData]);
      }, 500);
    });
  },

  /**
   * Get account details by ID
   * @param {string} accountId - The account ID
   * @returns {Promise<Object|null>} - Promise resolving to account details or null if not found
   */
  getAccountById: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const account = mockAccountsData.find((acc) => acc.id === accountId);
        resolve(account || null);
      }, 500);
    });
  },

  /**
   * Create a new account
   * @param {Object} accountData - The account data to create
   * @returns {Promise<Object>} - Promise resolving to the created account
   */
  createAccount: (accountData) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const newId = (mockAccountsData.length + 1).toString();
        const newAccount = {
          id: newId,
          ...accountData,
          created_at: new Date().toISOString(),
          last_updated: new Date().toISOString(),
        };

        mockAccountsData.push(newAccount);

        // Also create mock metrics
        mockAccountMetricsData[newId] = {
          balance: "$0.00",
          performance: 0,
        };

        resolve(newAccount);
      }, 500);
    });
  },

  /**
   * Update an existing account
   * @param {string} accountId - The ID of the account to update
   * @param {Object} accountData - The updated account data
   * @returns {Promise<Object>} - Promise resolving to the updated account
   */
  updateAccount: (accountId, accountData) => {
    return new Promise((resolve, reject) => {
      // Simulate network delay
      setTimeout(() => {
        const accountIndex = mockAccountsData.findIndex(
          (acc) => acc.id === accountId
        );

        if (accountIndex === -1) {
          reject(new Error(`Account with ID ${accountId} not found`));
          return;
        }

        const updatedAccount = {
          ...mockAccountsData[accountIndex],
          ...accountData,
          last_updated: new Date().toISOString(),
        };

        mockAccountsData[accountIndex] = updatedAccount;
        resolve(updatedAccount);
      }, 500);
    });
  },

  /**
   * Delete an account
   * @param {string} accountId - The ID of the account to delete
   * @returns {Promise<boolean>} - Promise resolving to success status
   */
  deleteAccount: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const accountIndex = mockAccountsData.findIndex(
          (acc) => acc.id === accountId
        );

        if (accountIndex === -1) {
          resolve(false);
          return;
        }

        mockAccountsData.splice(accountIndex, 1);

        // Also remove metrics
        delete mockAccountMetricsData[accountId];

        resolve(true);
      }, 500);
    });
  },

  /**
   * Get account balance and performance metrics
   * @param {string} accountId - The ID of the account
   * @returns {Promise<Object>} - Promise resolving to account metrics
   */
  getAccountMetrics: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        resolve(
          mockAccountMetricsData[accountId] || {
            balance: "N/A",
            performance: 0,
          }
        );
      }, 500);
    });
  },
};

export default AccountsAPI;
