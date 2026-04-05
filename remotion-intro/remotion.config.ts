import { Config } from "@remotion/cli/config";

Config.overrideWebpackConfig((config) => {
  return {
    ...config,
    output: {
      ...config.output,
      hashFunction: "xxhash64", // WASMを使わないハッシュ関数を指定
    },
  };
});
