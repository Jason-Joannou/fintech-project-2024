export interface IEnvVariables {
  backendUrl: string;
  ilpUrl: string;
}

export const getEnviromentVariables = (): IEnvVariables => {
  const variables = {
    backendUrl: process.env.BACKEND_URL || "http://localhost:3000",
    ilpUrl: process.env.ILP_URL || "http://localhost:3001",
  };

  return variables;
};
