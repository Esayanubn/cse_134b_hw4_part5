function createBuildTimeAstroVersionProvider() {
  const version = "5.15.8";
  return {
    getVersion() {
      return version;
    }
  };
}
export {
  createBuildTimeAstroVersionProvider
};
