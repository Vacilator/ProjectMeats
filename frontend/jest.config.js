/**
 * Jest configuration for ProjectMeats frontend
 * Fixes ES6 module issues with axios and other dependencies
 */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  // Transform ES6 modules from node_modules that cause issues
  transformIgnorePatterns: [
    'node_modules/(?!(axios)/)',
  ],
  // Collect coverage from src files
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/setupTests.ts',
  ],
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};