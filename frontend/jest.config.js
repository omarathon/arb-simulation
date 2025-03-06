module.exports = {
    preset: "ts-jest",
    testEnvironment: "jsdom",
    testMatch: [
      "**/__tests__/**/*.[jt]s?(x)",
      "**/?(*.)+(spec|test).[tj]s?(x)"
    ],
    moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
    transformIgnorePatterns: ["<rootDir>/node_modules/"],
    watchPathIgnorePatterns: ["/node_modules/", "/dist/", "/build/"]
  };
  