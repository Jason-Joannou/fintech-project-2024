import axios from "axios";
import { getEnviromentVariables } from "../enviroment";

const getBackendUrl = () => {
  const { backendUrl } = getEnviromentVariables();
  const apiVersion = "v1";
  const fullUrl = `${backendUrl}/${apiVersion}`;
  return fullUrl;
};

const getIlpUrl = () => {
  // for testing
  const { ilpUrl } = getEnviromentVariables();
  const apiVersion = "v1";
  const fullUrl = `${ilpUrl}/${apiVersion}`;
  return fullUrl;
};

const createAxiosInstance = (baseURL: string) =>
  axios.create({
    baseURL: baseURL,
  });

export { getBackendUrl, getIlpUrl, createAxiosInstance };
